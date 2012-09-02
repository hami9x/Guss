import post, utils, config

class TopicModel(post.MasterPostModel):
    def default_pagination(self, page=1):
        self.pagination = utils.NumberedPagination(model_cls=ReplyModel,
                limit=config.get_config("forum_replies_per_page"),
                order="created",
                page=page,
                master=self
                )

class ReplyModel(post.SlavePostModel):
    pass
