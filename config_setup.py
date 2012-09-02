import config, utils

def default_configs():
    return [
            config.StringValue("site_name", "Name", True),
            config.StringValue("session_secret_key", utils.generate_random_string(30), False),
            config.StringValue("admin_email", "admin@gmail.com", True),
            config.BooleanValue("user_email_confirm", False, True),
            config.IntegerValue("blog_comments_per_page", 20, True),
            config.IntegerValue("forum_replies_per_page", 20, True),
        ]
