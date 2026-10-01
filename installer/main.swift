// Dungeon Siege Installer
//
// Builds a self-contained "Dungeon Siege LoA.app": downloads a Wine engine and
// wrapper libraries, runs the user's own GOG installer inside it, adds
// dgVoodoo 2.53 and DXVK-macOS, applies the SSE performance patch, and writes
// a small launcher. Every download and every patched file is checked by SHA-256.

import AppKit
import CryptoKit
import UniformTypeIdentifiers

// MARK: - Manifest

struct Download: Decodable {
    let url: String
    let sha256: String
    let bytes: Int?
    let version: String?
    let name: String?
    let files: [String: [String]]?
}

struct PatchedFile: Decodable {
    let patch: String
    let original: String
    let patched: String
}

struct Manifest: Decodable {
    let files: [String: PatchedFile]
    let requires: [String: String]
    let renderer: [String: Download]
    let runtime: [String: Download]
}

enum InstallError: LocalizedError {
    case message(String)
    var errorDescription: String? { if case .message(let m) = self { return m }; return nil }
}

func fail(_ m: String) -> InstallError { .message(m) }

// MARK: - Helpers

let fm = FileManager.default
let resources = Bundle.main.resourceURL!
let manifest: Manifest = {
    let data = try! Data(contentsOf: resources.appendingPathComponent("manifest.json"))
    return try! JSONDecoder().decode(Manifest.self, from: data)
}()

func sha256(_ data: Data) -> String {
    SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}

func sha256(file: URL) -> String? {
    guard let h = FileHandle(forReadingAtPath: file.path) else { return nil }
    defer { try? h.close() }
    var hasher = SHA256()
    while let chunk = try? h.read(upToCount: 8 << 20), !chunk.isEmpty { hasher.update(data: chunk) }
    return hasher.finalize().map { String(format: "%02x", $0) }.joined()
}

@discardableResult
func run(_ tool: String, _ args: [String], env: [String: String]? = nil, cwd: URL? = nil, logTo: URL? = nil) throws -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: tool)
    p.arguments = args
    if let env { p.environment = env }
    if let cwd { p.currentDirectoryURL = cwd }
    if let logTo {
        // Wine's helper processes inherit stdout; a file never blocks the way a pipe would.
        if !fm.fileExists(atPath: logTo.path) { fm.createFile(atPath: logTo.path, contents: nil) }
        let h = try FileHandle(forWritingTo: logTo)
        h.seekToEndOfFile()
        p.standardOutput = h
        p.standardError = h
        try p.run()
        p.waitUntilExit()
        try? h.close()
        if p.terminationStatus != 0 { throw fail("\(URL(fileURLWithPath: tool).lastPathComponent) failed (\(p.terminationStatus)). Details: \(logTo.path)") }
        return ""
    }
    let pipe = Pipe()
    p.standardOutput = pipe
    p.standardError = pipe
    try p.run()
    let out = pipe.fileHandleForReading.readDataToEndOfFile()
    p.waitUntilExit()
    let text = String(decoding: out, as: UTF8.self)
    if p.terminationStatus != 0 {
        throw fail("\(URL(fileURLWithPath: tool).lastPathComponent) failed (\(p.terminationStatus)): \(text.suffix(400))")
    }
    return text
}

// Case-insensitive file lookup; Windows installers don't care about case.
func find(_ folder: URL, _ name: String) -> URL {
    if let items = try? fm.contentsOfDirectory(atPath: folder.path),
       let hit = items.first(where: { $0.lowercased() == name.lowercased() }) {
        return folder.appendingPathComponent(hit)
    }
    return folder.appendingPathComponent(name)
}

// MARK: - BPS

func readNumber(_ d: [UInt8], _ pos: inout Int) -> Int {
    var value = 0, shift = 1
    while true {
        let b = Int(d[pos]); pos += 1
        value += (b & 0x7f) * shift
        if b & 0x80 != 0 { return value }
        shift <<= 7
        value += shift
    }
}

func crc32(_ bytes: [UInt8]) -> UInt32 {
    var table = [UInt32](repeating: 0, count: 256)
    for i in 0..<256 {
        var c = UInt32(i)
        for _ in 0..<8 { c = (c & 1) != 0 ? 0xEDB88320 ^ (c >> 1) : c >> 1 }
        table[i] = c
    }
    var crc: UInt32 = 0xFFFFFFFF
    for b in bytes { crc = table[Int((crc ^ UInt32(b)) & 0xff)] ^ (crc >> 8) }
    return crc ^ 0xFFFFFFFF
}

func le32(_ d: [UInt8], _ at: Int) -> UInt32 {
    UInt32(d[at]) | UInt32(d[at + 1]) << 8 | UInt32(d[at + 2]) << 16 | UInt32(d[at + 3]) << 24
}

func applyBPS(source: [UInt8], patch: [UInt8]) throws -> [UInt8] {
    guard patch.count > 16, Array(patch[0..<4]) == Array("BPS1".utf8) else { throw fail("Not a BPS patch.") }
    guard crc32(Array(patch[0..<(patch.count - 4)])) == le32(patch, patch.count - 4) else { throw fail("The patch file is damaged.") }
    guard crc32(source) == le32(patch, patch.count - 12) else { throw fail("The game file doesn't match the patch.") }
    var pos = 4
    let sourceSize = readNumber(patch, &pos)
    let targetSize = readNumber(patch, &pos)
    pos += readNumber(patch, &pos)
    guard sourceSize == source.count else { throw fail("The game file size doesn't match the patch.") }
    var out = [UInt8](); out.reserveCapacity(targetSize)
    var sourceRel = 0, targetRel = 0
    let end = patch.count - 12
    while pos < end {
        let data = readNumber(patch, &pos)
        let action = data & 3, length = (data >> 2) + 1
        switch action {
        case 0: out.append(contentsOf: source[out.count..<(out.count + length)])
        case 1: out.append(contentsOf: patch[pos..<(pos + length)]); pos += length
        default:
            let raw = readNumber(patch, &pos)
            let offset = (raw & 1) != 0 ? -(raw >> 1) : raw >> 1
            if action == 2 {
                sourceRel += offset
                out.append(contentsOf: source[sourceRel..<(sourceRel + length)])
                sourceRel += length
            } else {
                targetRel += offset
                for _ in 0..<length { out.append(out[targetRel]); targetRel += 1 }
            }
        }
    }
    guard out.count == targetSize, crc32(out) == le32(patch, patch.count - 8) else { throw fail("The patched file failed its checksum.") }
    return out
}

// MARK: - Installer

final class Installer {
    let source: URL                     // GOG setup .exe, or an existing game folder
    let loaZip: URL?                    // community "Legends of Aranna fix" zip (with the GOG installer)
    let target: URL                     // final .app location
    let log: (String) -> Void
    let progress: (Double?, String) -> Void

    let cache = fm.urls(for: .cachesDirectory, in: .userDomainMask)[0].appendingPathComponent("DungeonSiegeInstaller")
    lazy var build = target.deletingLastPathComponent().appendingPathComponent(".\(target.lastPathComponent).building")
    var contents: URL { build.appendingPathComponent("Contents") }
    var wineBin: URL { contents.appendingPathComponent("SharedSupport/wine/bin") }
    var prefix: URL { contents.appendingPathComponent("SharedSupport/prefix") }
    var game: URL { prefix.appendingPathComponent("drive_c/GOG Games/Dungeon Siege") }

    init(source: URL, loaZip: URL?, target: URL, log: @escaping (String) -> Void, progress: @escaping (Double?, String) -> Void) {
        self.source = source; self.loaZip = loaZip; self.target = target; self.log = log; self.progress = progress
    }

    var wineEnv: [String: String] {
        var e = ProcessInfo.processInfo.environment
        e["WINEPREFIX"] = prefix.path
        e["DYLD_FALLBACK_LIBRARY_PATH"] = [contents.appendingPathComponent("SharedSupport/wine/lib").path,
                                           contents.appendingPathComponent("Frameworks").path,
                                           contents.appendingPathComponent("Frameworks/GStreamer.framework/Libraries").path,
                                           "/usr/lib"].joined(separator: ":")
        e["WINEDEBUG"] = "-all"
        e["WINEESYNC"] = "1"
        e["WINEMSYNC"] = "1"
        return e
    }

    var wineLog: URL { cache.appendingPathComponent("wine.log") }

    func wine(_ args: [String], cwd: URL? = nil) throws {
        try run(wineBin.appendingPathComponent("wine").path, args, env: wineEnv, cwd: cwd, logTo: wineLog)
    }

    func waitForWine() {
        _ = try? run(wineBin.appendingPathComponent("wineserver").path, ["-w"], env: wineEnv, logTo: wineLog)
    }

    // Downloads to the cache, resuming nothing but skipping files already verified.
    func fetch(_ d: Download, label: String, weight: (Double, Double)) throws -> URL {
        try fm.createDirectory(at: cache, withIntermediateDirectories: true)
        let file = cache.appendingPathComponent(URL(string: d.url)!.lastPathComponent)
        if sha256(file: file) == d.sha256 { log("\(label): already downloaded"); return file }
        try? fm.removeItem(at: file)
        log("Downloading \(label)")
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/usr/bin/curl")
        p.arguments = ["-fsSL", "--retry", "3", "-o", file.path, d.url]
        try p.run()
        while p.isRunning {
            if let total = d.bytes, let size = (try? fm.attributesOfItem(atPath: file.path))?[.size] as? Int {
                let f = min(1, Double(size) / Double(total))
                progress(weight.0 + (weight.1 - weight.0) * f, "Downloading \(label)… \(Int(f * 100))%")
            }
            Thread.sleep(forTimeInterval: 0.25)
        }
        guard p.terminationStatus == 0 else { throw fail("Couldn't download \(label). Check your internet connection and try again.") }
        guard sha256(file: file) == d.sha256 else {
            try? fm.removeItem(at: file)
            throw fail("\(label) didn't match its expected checksum. Nothing was installed; try again.")
        }
        return file
    }

    func extract(_ archive: URL, into dir: URL) throws {
        try fm.createDirectory(at: dir, withIntermediateDirectories: true)
        try run("/usr/bin/tar", ["-xf", archive.path, "-C", dir.path])
    }

    @discardableResult
    func install() throws -> String? {
        let rt = manifest.runtime, rd = manifest.renderer
        let template = try fetch(rt["template"]!, label: "wrapper libraries", weight: (0.00, 0.20))
        let engine = try fetch(rt["engine"]!, label: "Wine 10", weight: (0.20, 0.50))
        let dgv = try fetch(rd["dgvoodoo"]!, label: "dgVoodoo 2.53", weight: (0.50, 0.52))
        let dxvk = try fetch(rd["dxvk"]!, label: "DXVK 1.10.3", weight: (0.52, 0.54))

        progress(0.55, "Building the app…")
        try? fm.removeItem(at: build)
        let scratch = cache.appendingPathComponent("unpack")
        try? fm.removeItem(at: scratch)
        try extract(template, into: scratch)
        try extract(engine, into: scratch)
        let templateApp = try fm.contentsOfDirectory(at: scratch, includingPropertiesForKeys: nil)
            .first { $0.pathExtension == "app" }!
        try fm.createDirectory(at: contents.appendingPathComponent("MacOS"), withIntermediateDirectories: true)
        try fm.createDirectory(at: contents.appendingPathComponent("Resources"), withIntermediateDirectories: true)
        try fm.createDirectory(at: contents.appendingPathComponent("SharedSupport"), withIntermediateDirectories: true)
        try fm.moveItem(at: templateApp.appendingPathComponent("Contents/Frameworks"), to: contents.appendingPathComponent("Frameworks"))
        try fm.moveItem(at: scratch.appendingPathComponent("wswine.bundle"), to: contents.appendingPathComponent("SharedSupport/wine"))
        try? fm.removeItem(at: scratch)
        try writeLauncher()

        progress(nil, "Setting up Windows inside the app (about a minute)…")
        log("Creating the Wine prefix")
        try wine(["wineboot", "--init"])
        waitForWine()
        try keepUserFoldersInside()

        progress(nil, "Installing Dungeon Siege from your GOG installer (a few minutes)…")
        try installGame()
        waitForWine()
        guard fm.fileExists(atPath: find(game, "DSLOA.exe").path) else {
            throw fail("Legends of Aranna (DSLOA.exe) isn't installed. Choose the \"Legends of Aranna fix\" zip when asked.")
        }

        progress(0.85, "Adding dgVoodoo and DXVK…")
        try installRenderer(dgvoodoo: dgv, dxvk: dxvk)
        try setDllOverrides()

        progress(0.92, "Applying the performance patch…")
        var warning: String?
        do { try patchGame() } catch { warning = error.localizedDescription; log("Not patched: \(warning!)") }
        try setIcon()

        progress(0.98, "Finishing…")
        if fm.fileExists(atPath: target.path) {
            try fm.trashItem(at: target, resultingItemURL: nil)
        }
        try fm.moveItem(at: build, to: target)
        log("Installed \(target.path)")
        return warning
    }

    func writeLauncher() throws {
        let script = """
        #!/bin/bash
        # Launches Dungeon Siege: Legends of Aranna with the bundled Wine.
        APP="$(cd "$(dirname "$0")/../.." && pwd)"
        export WINEPREFIX="$APP/Contents/SharedSupport/prefix"
        export DYLD_FALLBACK_LIBRARY_PATH="$APP/Contents/SharedSupport/wine/lib:$APP/Contents/Frameworks:$APP/Contents/Frameworks/GStreamer.framework/Libraries:/usr/lib"
        export WINEDEBUG=-all WINEESYNC=1 WINEMSYNC=1
        cd "$WINEPREFIX/drive_c/GOG Games/Dungeon Siege" || exit 1
        while true; do
          "$APP/Contents/SharedSupport/wine/bin/wine" DSLOA.exe nointro=true fullscreen=false nospacecheck=true bltonly=true
          "$APP/Contents/SharedSupport/wine/bin/wineserver" -w
          # The game sets FIRSTRUN=1 under this key when the license is accepted, 0 when declined.
          grep -A3 -F 'Dungeon Siege\\\\Eula]' "$WINEPREFIX/user.reg" | grep -qF '"FIRSTRUN"=dword:00000001' && exit 0
          choice=$(/usr/bin/osascript -e 'button returned of (display dialog "Dungeon Siege closed because its license agreement was not accepted. You need to click Accept to play." buttons {"Quit", "Show It Again"} default button "Show It Again" with title "Dungeon Siege LoA" with icon caution)') || exit 0
          [ "$choice" = "Show It Again" ] || exit 0
        done
        """
        let launcher = contents.appendingPathComponent("MacOS/launch")
        try script.write(to: launcher, atomically: true, encoding: .utf8)
        try fm.setAttributes([.posixPermissions: 0o755], ofItemAtPath: launcher.path)
        let plist: [String: Any] = [
            "CFBundleExecutable": "launch",
            "CFBundleIdentifier": "io.github.idubichev.dungeonsiege-loa",
            "CFBundleName": "Dungeon Siege LoA",
            "CFBundleDisplayName": "Dungeon Siege LoA",
            "CFBundleIconFile": "AppIcon",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1",
            "LSMinimumSystemVersion": "13.0",
            "NSHighResolutionCapable": true,
        ]
        let data = try PropertyListSerialization.data(fromPropertyList: plist, format: .xml, options: 0)
        try data.write(to: contents.appendingPathComponent("Info.plist"))
    }

    // Wine links Desktop, Documents and friends to the Mac's own folders. Replace those
    // links with real folders so saves stay inside the app and macOS never asks for
    // access to Documents.
    func keepUserFoldersInside() throws {
        let users = prefix.appendingPathComponent("drive_c/users")
        for user in (try? fm.contentsOfDirectory(at: users, includingPropertiesForKeys: nil)) ?? [] {
            for item in (try? fm.contentsOfDirectory(at: user, includingPropertiesForKeys: nil)) ?? [] {
                if let dest = try? fm.destinationOfSymbolicLink(atPath: item.path), dest.hasPrefix("/") {
                    try fm.removeItem(at: item)
                    try fm.createDirectory(at: item, withIntermediateDirectories: true)
                }
            }
        }
    }

    func installGame() throws {
        var isDir: ObjCBool = false
        fm.fileExists(atPath: source.path, isDirectory: &isDir)
        if isDir.boolValue {
            log("Copying the game from \(source.path)")
            try fm.createDirectory(at: game.deletingLastPathComponent(), withIntermediateDirectories: true)
            try run("/bin/cp", ["-cR", source.path, game.path])
            for name in ["DDraw.dll", "D3DImm.dll", "d3d11.dll", "d3d10core.dll", "dxvk.conf", "dspatch-backup"] {
                try? fm.removeItem(at: find(game, name))
            }
        } else {
            // Under Wine, GOG's installer sometimes spends its first pass on DirectX and
            // exits early, so run it again until the base game is really there.
            for attempt in 1...3 {
                log("Running the GOG installer silently (pass \(attempt))")
                try wine([source.path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/NOICONS",
                          "/DIR=C:\\GOG Games\\Dungeon Siege"], cwd: source.deletingLastPathComponent())
                waitForWine()
                if baseGameComplete() { break }
            }
            guard baseGameComplete() else {
                throw fail("The GOG installer didn't finish installing the game. Make sure its .bin file is in the same folder as the .exe.")
            }
        }
        guard let loaZip else { return }
        progress(nil, "Adding Legends of Aranna…")
        log("Adding the Legends of Aranna fix")
        let scratch = cache.appendingPathComponent("loa")
        try? fm.removeItem(at: scratch)
        try fm.createDirectory(at: scratch, withIntermediateDirectories: true)
        try run("/usr/bin/ditto", ["-x", "-k", loaZip.path, scratch.path])
        guard let root = fm.enumerator(at: scratch, includingPropertiesForKeys: nil)?
                .compactMap({ $0 as? URL }).first(where: { $0.lastPathComponent.lowercased() == "dsloa.exe" })?
                .deletingLastPathComponent() else {
            throw fail("That zip doesn't contain DSLOA.exe. Choose the \"Legends of Aranna fix\" zip from the GenesisFR guide.")
        }
        try run("/bin/cp", ["-R", root.path + "/.", game.path])
        try? fm.removeItem(at: scratch)
    }

    func baseGameComplete() -> Bool {
        fm.fileExists(atPath: find(game, "DungeonSiege.exe").path) &&
        fm.fileExists(atPath: find(game, "DSVideoConfig.exe").path) &&
        fm.fileExists(atPath: find(game, "Resources").path)
    }

    func installRenderer(dgvoodoo: URL, dxvk: URL) throws {
        let scratch = cache.appendingPathComponent("renderer")
        try? fm.removeItem(at: scratch)
        try extract(dgvoodoo, into: scratch)
        try extract(dxvk, into: scratch)
        for key in ["dgvoodoo", "dxvk"] {
            for (name, spec) in manifest.renderer[key]!.files! {
                let file = scratch.appendingPathComponent(spec[0])
                guard sha256(file: file) == spec[1] else { throw fail("\(name) isn't the expected build.") }
                let dest = find(game, name)
                try? fm.removeItem(at: dest)
                try fm.copyItem(at: file, to: dest)
                log("Installed \(name)")
            }
        }
        try? fm.removeItem(at: scratch)
        let conf = find(game, "dxvk.conf")
        try? fm.removeItem(at: conf)
        try fm.copyItem(at: resources.appendingPathComponent("dxvk.conf"), to: conf)
    }

    func setDllOverrides() throws {
        waitForWine()
        let reg = prefix.appendingPathComponent("user.reg")
        var lines = (try String(contentsOf: reg, encoding: .utf8)).components(separatedBy: "\n")
        let header = "[Software\\\\Wine\\\\DllOverrides]"
        var at = lines.firstIndex { $0.hasPrefix(header) }
        if at == nil {
            let stamp = Int(Date().timeIntervalSince1970)
            lines += ["\(header) \(stamp)", String(format: "#time=%llx", (UInt64(stamp) + 11644473600) * 10_000_000), ""]
            at = lines.count - 3
        }
        var insert = at! + 1
        while insert < lines.count && lines[insert].hasPrefix("#") { insert += 1 }
        for name in ["ddraw", "d3dim", "d3d8", "d3d11", "d3d10core"] {
            lines.removeAll { $0.hasPrefix("\"\(name)\"=") }
            lines.insert("\"\(name)\"=\"native,builtin\"", at: insert)
        }
        try lines.joined(separator: "\n").write(to: reg, atomically: true, encoding: .utf8)
        log("Set Wine to use dgVoodoo and DXVK")
    }

    func patchGame() throws {
        for (name, required) in manifest.requires {
            guard sha256(file: find(game, name)) == required else { throw fail("\(name) isn't dgVoodoo 2.53.") }
        }
        let backup = game.appendingPathComponent("dspatch-backup")
        try fm.createDirectory(at: backup, withIntermediateDirectories: true)
        for (name, entry) in manifest.files {
            let file = find(game, name)
            let digest = sha256(file: file)
            if digest == entry.patched { continue }
            guard digest == entry.original else {
                throw fail("This copy of \(name) isn't the GOG release the patch was made for, so it was left unpatched. The game is installed and runs at normal speed.")
            }
            let original = try Data(contentsOf: file)
            let patch = try Data(contentsOf: resources.appendingPathComponent(entry.patch))
            let result = Data(try applyBPS(source: [UInt8](original), patch: [UInt8](patch)))
            guard sha256(result) == entry.patched else { throw fail("Patched \(name) failed verification.") }
            try original.write(to: backup.appendingPathComponent(name))
            try result.write(to: file)
            log("Patched \(name)")
        }
    }

    func setIcon() throws {
        let ico = (try? fm.contentsOfDirectory(at: game, includingPropertiesForKeys: nil))?
            .first { $0.lastPathComponent.hasPrefix("goggame-") && $0.pathExtension == "ico" }
        guard let ico else { return }
        _ = try? run("/usr/bin/sips", ["-s", "format", "icns", ico.path, "--out",
                                       contents.appendingPathComponent("Resources/AppIcon.icns").path])
    }
}

// MARK: - Window

final class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    let status = NSTextField(labelWithString: "")
    let bar = NSProgressIndicator()
    let logView = NSTextView()
    let primary = NSButton(title: "Install", target: nil, action: nil)
    let secondary = NSButton(title: "Where do I get the files?", target: nil, action: nil)
    var installed: URL?

    func applicationDidFinishLaunching(_ n: Notification) {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 470),
                          styleMask: [.titled, .closable, .miniaturizable], backing: .buffered, defer: false)
        window.title = "Dungeon Siege Installer"
        window.center()

        let title = NSTextField(labelWithString: "Dungeon Siege: Legends of Aranna")
        title.font = .boldSystemFont(ofSize: 20)
        let blurb = NSTextField(wrappingLabelWithString:
            "Installs Dungeon Siege: Legends of Aranna as a Mac app, with the performance patch that takes it from about 19 FPS to about 95.\n\n" +
            "You need Dungeon Siege (the GOG installer, or the game already installed from Steam or GOG) and the \"Legends of Aranna fix\" zip. " +
            "Put them in Downloads and click Install. Everything else is automatic and takes about 5 to 10 minutes.")
        blurb.textColor = .secondaryLabelColor

        status.stringValue = "Click Install to begin."
        status.font = .systemFont(ofSize: 13, weight: .medium)
        bar.isIndeterminate = false
        bar.minValue = 0; bar.maxValue = 1
        bar.style = .bar

        logView.isEditable = false
        logView.font = .monospacedSystemFont(ofSize: 11, weight: .regular)
        logView.textColor = .secondaryLabelColor
        let scroll = NSScrollView()
        scroll.documentView = logView
        scroll.hasVerticalScroller = true
        scroll.borderType = .bezelBorder
        logView.autoresizingMask = [.width]
        scroll.heightAnchor.constraint(equalToConstant: 150).isActive = true

        primary.bezelStyle = .rounded
        primary.keyEquivalent = "\r"
        primary.target = self; primary.action = #selector(choose)
        secondary.bezelStyle = .rounded
        secondary.target = self; secondary.action = #selector(help)
        let buttons = NSStackView(views: [secondary, NSView(), primary])
        buttons.distribution = .fill

        let stack = NSStackView(views: [title, blurb, status, bar, scroll, buttons])
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 14
        stack.edgeInsets = NSEdgeInsets(top: 24, left: 24, bottom: 20, right: 24)
        for v in [blurb, bar, scroll, buttons] { v.widthAnchor.constraint(equalTo: stack.widthAnchor, constant: -48).isActive = true }
        window.contentView = stack
        window.setContentSize(NSSize(width: 600, height: stack.fittingSize.height))
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ s: NSApplication) -> Bool { true }

    func append(_ line: String) {
        DispatchQueue.main.async {
            self.logView.string += line + "\n"
            self.logView.scrollToEndOfDocument(nil)
        }
    }

    func alert(_ title: String, _ text: String, buttons: [String] = ["OK"]) -> NSApplication.ModalResponse {
        let a = NSAlert()
        a.messageText = title
        a.informativeText = text
        buttons.forEach { a.addButton(withTitle: $0) }
        return a.runModal()
    }

    func rosettaReady() -> Bool {
        var info = utsname(); uname(&info)
        let machine = withUnsafeBytes(of: &info.machine) { String(decoding: $0.prefix { $0 != 0 }, as: UTF8.self) }
        if machine != "arm64" { return true }
        if (try? run("/usr/bin/arch", ["-x86_64", "/usr/bin/true"])) != nil { return true }
        guard alert("Rosetta is needed", "Dungeon Siege is a Windows game for Intel processors. macOS needs Rosetta to run it. Install it now? You'll be asked for your password.",
                    buttons: ["Install Rosetta", "Cancel"]) == .alertFirstButtonReturn else { return false }
        let script = NSAppleScript(source: "do shell script \"/usr/sbin/softwareupdate --install-rosetta --agree-to-license\" with administrator privileges")
        var error: NSDictionary?
        script?.executeAndReturnError(&error)
        return error == nil && (try? run("/usr/bin/arch", ["-x86_64", "/usr/bin/true"])) != nil
    }

    var downloads: URL { fm.urls(for: .downloadsDirectory, in: .userDomainMask)[0] }

    static let guide = URL(string: "https://github.com/idubichev/dungeon-siege-loa-optimizations/blob/main/INSTALL.md")!
    static let loaPage = URL(string: "https://gist.github.com/GenesisFR/f3df7f092db17dd63d85eb1f19da7153#-links-")!

    @objc func help() { NSWorkspace.shared.open(AppDelegate.guide) }

    // Existing installs of the base game: Wine wrappers, CrossOver and Whisky bottles,
    // Steam or GOG folders, or a folder copied from a Windows PC into Downloads or Desktop.
    func existingInstalls() -> [URL] {
        let home = fm.homeDirectoryForCurrentUser
        let prefixes = ["Applications/*.app/Contents/SharedSupport/prefix", "Applications/*/*.app/Contents/SharedSupport/prefix",
                        "Library/Application Support/CrossOver/Bottles/*",
                        "Library/Containers/com.isaacmarovitz.Whisky/Bottles/*"]
        let inside = ["drive_c/GOG Games/Dungeon Siege*", "drive_c/Program Files*/Steam/steamapps/common/Dungeon Siege*",
                      "drive_c/Program Files*/GOG Galaxy/Games/Dungeon Siege*", "drive_c/Program Files*/Microsoft Games/Dungeon Siege*"]
        var patterns = prefixes.flatMap { p in inside.map { "\(p)/\($0)" } }
        patterns += ["Downloads/Dungeon Siege*", "Desktop/Dungeon Siege*", "Downloads/*/Dungeon Siege*"]
        var found: [URL] = []
        for pattern in patterns {
            for match in glob(home.appendingPathComponent(pattern).path) where !match.contains("Dungeon Siege LoA.app") {
                let url = URL(fileURLWithPath: match)
                if fm.fileExists(atPath: find(url, "DungeonSiege.exe").path) || fm.fileExists(atPath: find(url, "DSLOA.exe").path) {
                    found.append(url)
                }
            }
        }
        return found
    }

    func glob(_ pattern: String) -> [String] {
        var g = glob_t()
        defer { globfree(&g) }
        guard Darwin.glob(pattern, 0, nil, &g) == 0 else { return [] }
        return (0..<Int(g.gl_pathc)).compactMap { g.gl_pathv[$0].flatMap { String(cString: $0) } }
    }

    func hasPatchableLoA(_ folder: URL) -> Bool {
        let digest = sha256(file: find(folder, "DSLOA.exe"))
        return digest == manifest.files["DSLOA.exe"]!.original || digest == manifest.files["DSLOA.exe"]!.patched
    }

    func newest(in dir: URL, _ match: (String) -> Bool) -> URL? {
        ((try? fm.contentsOfDirectory(at: dir, includingPropertiesForKeys: [.contentModificationDateKey])) ?? [])
            .filter { match($0.lastPathComponent.lowercased()) }
            .max { (a, b) in
                ((try? a.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast) <
                ((try? b.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast) }
    }

    func isGOGInstaller(_ n: String) -> Bool { n.hasPrefix("setup_dungeon_siege_1") && n.hasSuffix(".exe") }
    func isLoAZip(_ n: String) -> Bool { n.hasSuffix(".zip") && n.contains("aranna") }

    @objc func choose() {
        if let installed { NSWorkspace.shared.open(installed); NSApp.terminate(nil); return }

        // 1. The game: GOG installer in Downloads, else an existing install, else ask.
        var source: URL? = newest(in: downloads, isGOGInstaller)
        if source == nil {
            let installs = existingInstalls()
            source = installs.first { hasPatchableLoA($0) } ?? installs.first
        }
        if source == nil {
            let panel = NSOpenPanel()
            panel.title = "Where is Dungeon Siege?"
            panel.message = "Choose the GOG installer (setup_dungeon_siege_1….exe) or your Dungeon Siege folder from Steam or GOG."
            panel.canChooseDirectories = true
            panel.directoryURL = downloads
            guard panel.runModal() == .OK, let url = panel.url else { return }
            source = url
        }
        guard let source else { return }
        var isDir: ObjCBool = false
        fm.fileExists(atPath: source.path, isDirectory: &isDir)
        if isDir.boolValue {
            guard fm.fileExists(atPath: find(source, "DungeonSiege.exe").path) || fm.fileExists(atPath: find(source, "DSLOA.exe").path) else {
                _ = alert("Dungeon Siege isn't in that folder", "Choose the folder that contains DungeonSiege.exe, or the GOG installer.")
                return
            }
        } else if !isGOGInstaller(source.lastPathComponent.lowercased()) {
            _ = alert("That doesn't look like the right file", "Choose the GOG installer for Dungeon Siege 1 (setup_dungeon_siege_1….exe) or your Dungeon Siege folder.")
            return
        }
        append("Game: \(source.path)")

        // 2. Legends of Aranna: required unless the folder already has the right DSLOA.exe.
        var loa: URL? = nil
        if !(isDir.boolValue && hasPatchableLoA(source)) {
            loa = newest(in: downloads, isLoAZip)
            if loa == nil {
                let choice = alert("One more download: Legends of Aranna",
                                   "The expansion comes from the community \"Legends of Aranna fix\" zip. Download it, then click Install again.",
                                   buttons: ["Open Download Page", "I Have It…", "Cancel"])
                if choice == .alertFirstButtonReturn { NSWorkspace.shared.open(AppDelegate.loaPage); return }
                guard choice == .alertSecondButtonReturn else { return }
                let panel = NSOpenPanel()
                panel.title = "Choose the Legends of Aranna fix"
                panel.allowedContentTypes = [UTType(filenameExtension: "zip") ?? .data]
                panel.directoryURL = downloads
                guard panel.runModal() == .OK, let url = panel.url else { return }
                loa = url
            }
            append("Legends of Aranna: \(loa!.path)")
        }
        start(source: source, loaZip: loa)
    }

    func start(source: URL, loaZip: URL?) {
        guard rosettaReady() else { return }
        let apps = fm.homeDirectoryForCurrentUser.appendingPathComponent("Applications")
        try? fm.createDirectory(at: apps, withIntermediateDirectories: true)
        let target = apps.appendingPathComponent("Dungeon Siege LoA.app")
        if fm.fileExists(atPath: target.path) {
            guard alert("Dungeon Siege LoA is already installed", "Replace it? The old copy, including its saved games, goes to the Trash.",
                        buttons: ["Replace", "Cancel"]) == .alertFirstButtonReturn else { return }
        }
        primary.isEnabled = false
        secondary.isEnabled = false
        let installer = Installer(source: source, loaZip: loaZip, target: target, log: { self.append($0) }, progress: { value, text in
            DispatchQueue.main.async {
                self.status.stringValue = text
                if let value { self.bar.isIndeterminate = false; self.bar.doubleValue = value; self.bar.stopAnimation(nil) }
                else { self.bar.isIndeterminate = true; self.bar.startAnimation(nil) }
            }
        })
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let warning = try installer.install()
                DispatchQueue.main.async {
                    if let warning { _ = self.alert("Installed without the patch", warning) }
                    self.bar.isIndeterminate = false; self.bar.doubleValue = 1
                    self.status.stringValue = "Done. Dungeon Siege LoA is in your Applications folder."
                    self.installed = target
                    self.primary.title = "Play Dungeon Siege"
                    self.primary.isEnabled = true
                    self.secondary.isHidden = true
                }
            } catch {
                self.append("Error: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self.bar.isIndeterminate = false; self.bar.doubleValue = 0
                    self.status.stringValue = "Installation stopped."
                    _ = self.alert("Installation stopped", error.localizedDescription)
                    self.primary.isEnabled = true
                    self.secondary.isEnabled = true
                }
            }
        }
    }
}

// Command-line mode, for testing and scripting:
//   "Dungeon Siege Installer" --install <GOG setup .exe or game folder> [--loa <fix.zip>] [--to <path/Name.app>]
let args = CommandLine.arguments
if args.contains("--detect") {
    let d = AppDelegate()
    print("GOG installer:", d.newest(in: d.downloads, d.isGOGInstaller)?.path ?? "none")
    print("LoA fix zip:  ", d.newest(in: d.downloads, d.isLoAZip)?.path ?? "none")
    for i in d.existingInstalls() { print("Existing:", i.path, d.hasPatchableLoA(i) ? "(has DSLOA.exe)" : "(base game only)") }
    exit(0)
}
if let i = args.firstIndex(of: "--install"), i + 1 < args.count {
    let source = URL(fileURLWithPath: args[i + 1])
    let target = args.firstIndex(of: "--to").map { URL(fileURLWithPath: args[$0 + 1]) }
        ?? fm.homeDirectoryForCurrentUser.appendingPathComponent("Applications/Dungeon Siege LoA.app")
    var last = ""
    let loa = args.firstIndex(of: "--loa").map { URL(fileURLWithPath: args[$0 + 1]) }
    let installer = Installer(source: source, loaZip: loa, target: target, log: { print($0) }, progress: { _, text in
        if text != last, !text.contains("%") { print("» " + text); last = text }
    })
    do {
        if let warning = try installer.install() { print("Warning: " + warning) }
        print("Done: " + target.path)
        exit(0)
    } catch {
        print("Error: " + error.localizedDescription)
        exit(1)
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
