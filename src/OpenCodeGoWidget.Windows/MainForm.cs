using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace OpenCodeGoWidget;

internal sealed class MainForm : Form
{
    private const string VirtualHost = "app.local";
    private readonly WebView2 _web = new() { Dock = DockStyle.Fill };
    private bool _ready;

    public MainForm()
    {
        Text = "OpenCode Go";
        ClientSize = new Size(620, 860);
        MinimumSize = SizeFromClientSize(new Size(620, 560));
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.Sizable;
        MaximizeBox = false;
        BackColor = Color.White;
        Icon = WebAssets.LoadAppIcon();

        Controls.Add(_web);
        Shown += async (_, _) => await InitializeWebViewAsync();
    }

    /// <summary>关闭窗口时收进托盘，不退出进程（和 macOS 版行为一致）。</summary>
    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        if (e.CloseReason == CloseReason.UserClosing)
        {
            e.Cancel = true;
            Hide();
        }
        base.OnFormClosing(e);
    }

    public async Task ShowPanelAsync(bool openSettings = false)
    {
        Show();
        if (WindowState == FormWindowState.Minimized) WindowState = FormWindowState.Normal;
        Activate();
        BringToFront();

        if (!_ready) return;
        if (openSettings)
            await _web.CoreWebView2.ExecuteScriptAsync("window.openSettings && window.openSettings()");
    }

    private async Task InitializeWebViewAsync()
    {
        if (_ready) return;

        var userDataFolder = Path.Combine(WebAssets.DataRoot, "webview2");
        Directory.CreateDirectory(userDataFolder);
        var environment = await CoreWebView2Environment.CreateAsync(userDataFolder: userDataFolder);
        await _web.EnsureCoreWebView2Async(environment);

        var core = _web.CoreWebView2;
        core.Settings.AreDefaultContextMenusEnabled = false;
        core.Settings.IsStatusBarEnabled = false;
        core.Settings.AreDevToolsEnabled = true;

        // 把本机释放出来的界面目录映射成 https 虚拟主机，相对路径（../design/tokens.css）才能正常解析
        core.SetVirtualHostNameToFolderMapping(
            VirtualHost, WebAssets.WebRoot, CoreWebView2HostResourceAccessKind.Allow);

        _ready = true;
        core.Navigate($"https://{VirtualHost}/prototype/index.html?embed=1");
    }
}
