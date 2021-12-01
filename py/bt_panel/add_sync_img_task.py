import os

from bt_panel_api import bt_panel

if __name__ == '__main__':
    PANEL_URL = str(os.environ.get("PANEL_URL"))
    PANEL_API_KEY = str(os.environ.get("PANEL_API_KEY"))
    my_panel = bt_panel(panel_url=PANEL_URL, panel_api_key=PANEL_API_KEY)
    print(
        my_panel.add_crontab_CRONTAB(
            post_name="同步img",
            post_hour="3",
            post_minute="30",
            post_sBody="sudo python3.10 /root/bingHD.py\nrsync -avzhP --update /onedrive/resource/img/ /www/wwwroot/img.dayepao.com/img/"
        )
    )
