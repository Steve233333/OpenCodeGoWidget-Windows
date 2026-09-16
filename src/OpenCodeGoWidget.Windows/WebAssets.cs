using System.Reflection;

namespace OpenCodeGoWidget;

/// <summary>
/// 界面文件以嵌入资源随 exe 一起发布，启动时释放到本机目录，
/// 再交给 WebView2 的虚拟主机映射。这样 exe 是单文件，不用带一堆散装文件。
/// </summary>
internal static class WebAssets
{
    private static readonly string Root =
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                     "OpenCodeGoWidget");

    public static string WebRoot => Path.Combine(Root, "web");
    public static string DataRoot => Path.Combine(Root, "data");

    /// <summary>把嵌入资源写到本机，返回是否发生过更新。</summary>
    public static bool Extract()
    {
        Directory.CreateDirectory(DataRoot);
        var wrote = false;
        wrote |= WriteResource("web.prototype.index.html", Path.Combine(WebRoot, "prototype", "index.html"));
        wrote |= WriteResource("web.design.tokens.css", Path.Combine(WebRoot, "design", "tokens.css"));
        return wrote;
    }

    public static Icon LoadAppIcon()
    {
        using var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("assets.app.ico");
        return stream is null ? SystemIcons.Application : new Icon(stream);
    }

    private static bool WriteResource(string resourceName, string targetPath)
    {
        using var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName);
        if (stream is null) return false;

        using var buffer = new MemoryStream();
        stream.CopyTo(buffer);
        var content = buffer.ToArray();

        // 内容没变就不重复写盘，避免每次启动都动文件
        if (File.Exists(targetPath) && File.ReadAllBytes(targetPath).AsSpan().SequenceEqual(content))
            return false;

        Directory.CreateDirectory(Path.GetDirectoryName(targetPath)!);
        File.WriteAllBytes(targetPath, content);
        return true;
    }
}
