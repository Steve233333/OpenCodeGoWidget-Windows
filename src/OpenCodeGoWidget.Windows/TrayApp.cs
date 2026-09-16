namespace OpenCodeGoWidget;

/// <summary>托盘常驻 + 主窗口，程序主体。</summary>
internal sealed class TrayApp : ApplicationContext
{
    private readonly NotifyIcon _tray;
    private readonly MainForm _window;

    public TrayApp()
    {
        WebAssets.Extract();

        _window = new MainForm();

        var menu = new ContextMenuStrip();
        menu.Items.Add("打开主面板", null, (_, _) => ShowPanel());
        menu.Items.Add("设置…", null, (_, _) => ShowPanel(openSettings: true));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add("退出", null, (_, _) => ExitApp());

        _tray = new NotifyIcon
        {
            Icon = WebAssets.LoadAppIcon(),
            Text = "OpenCode Go",
            Visible = true,
            ContextMenuStrip = menu,
        };
        // 左键点图标直接开面板；右键出菜单
        _tray.MouseClick += (_, e) =>
        {
            if (e.Button == MouseButtons.Left) ShowPanel();
        };

        ShowPanel();
    }

    private async void ShowPanel(bool openSettings = false)
    {
        try
        {
            await _window.ShowPanelAsync(openSettings);
        }
        catch (Exception ex)
        {
            MessageBox.Show(ex.Message, "OpenCode Go", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void ExitApp()
    {
        _tray.Visible = false;
        _tray.Dispose();
        _window.Dispose();
        ExitThread();
    }
}
