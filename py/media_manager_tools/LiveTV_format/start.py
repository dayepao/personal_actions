from livetv_format import create_app

app = create_app()

if __name__ == "__main__":
    from livetv_format.handle_cache import schedule_update_cached_file
    schedule_update_cached_file()
    app.run()
