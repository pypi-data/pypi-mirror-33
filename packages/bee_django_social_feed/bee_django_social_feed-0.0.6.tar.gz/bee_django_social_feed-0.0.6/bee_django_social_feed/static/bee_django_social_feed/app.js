$(document).ready(function () {
    var new_feed = new Vue({
        el: '#new-feed',
        data: {
            content: '',
            success_message: '',
            error_message: ''
        }
    });

    var feeds = new Vue({
        el: '#feeds',
        data: {
            feeds: [],
            page: 1,
            type: 0,   // 0 所有，1 单个用户, 2 同班同学（假的）
            user_id: 0,
            request_user_id: 0,
        },

        methods: {
            load_all_page: function (e) {
                e.preventDefault();
                feeds.user_id = 0;
                feeds.type = 0;
                feeds.page = 1;
                feeds.feeds = [];
                load_page_data();
            },

            load_classmates_page: function(user_id) {
                feeds.user_id = user_id;
                feeds.type = 2;
                feeds.page = 1;
                feeds.feeds = [];
                load_page_data();
            },

            load_my_page: function (user_id) {
                feeds.user_id = user_id;
                feeds.type = 1;
                feeds.page = 1;
                feeds.feeds = [];
                load_page_data();
            }
        }
    });

    var loader = new Vue({
        el: '#feeds-loader',
        data: {
            status: 0
        },

        methods: {
            load_more_page: function (e) {
                e.preventDefault();

                feeds.page++;
                loader.status = 1;
                load_page_data();
            }
        }
    });

    Vue.component('feed', {
        template: '#feed-template',
        props: ['id', 'publisher_data', 'content', 'emojis', 'comments', 'created_at', 'input_show'],
        data: function () {
            return {
                data_id: this.id,
                data_publisher: this.publisher_data,
                data_content: this.content,
                data_emojis: this.emojis,
                data_comments: this.comments,
                data_created_at: this.created_at,
                data_input_show: this.input_show,
                new_comment: ''
            };
        },

        computed: {
            // 当前登录用户，是否给该条feed点过赞了？
            is_request_user_emoji: function () {
                var rc = false;

                if (typeof(this.data_emojis) === "undefined") {
                    return rc;
                }

                this.data_emojis.forEach(function (i) {
                    if (i.user_id === feeds.request_user_id) {
                        rc = true;
                    }
                });

                return rc;
            },

            // 该条feed 是否有人点赞了？
            has_emojis: function () {
                if (typeof(this.data_emojis) === "undefined") {
                    return false;
                } else {
                    return this.data_emojis.length > 0;
                }
            },

            // 是否有评论了
            has_comments: function () {
                if (typeof(this.data_comments) === "undefined") {
                    return false;
                } else {
                    return this.data_comments.length > 0;
                }
            }
        },

        methods: {
            load_user_page: function (user_id, e) {
                e.preventDefault();
                feeds.user_id = user_id;
                feeds.type = 1;
                feeds.page = 1;
                feeds.feeds = [];
                load_page_data();
            },

            // 点赞
            post_emoji: function (feed_id) {
                var this_feed = this;
                $.post('/feed/feeds/' + String(feed_id) + '/emoji')
                    .done(function (data) {
                        this_feed.data_emojis = this_feed.data_emojis.concat(JSON.parse(data['new_emoji']));
                    })
            },

            // 显示feed的评论输入框
            show_comment_input: function () {
                if (this.data_input_show) {
                    this.data_input_show = false;
                } else {
                    this.data_input_show = true;
                }
            },

            // 发表对feed的评论
            post_comment: function (feed_id, comment) {
                var this_feed = this;
                var post_data = {
                    comment: comment
                };
                $.post('/feed/feeds/' + String(feed_id) + '/comment', post_data)
                    .done(function (data) {
                        this_feed.data_comments = this_feed.data_comments.concat(JSON.parse(data['new_comments']));
                        this_feed.new_comments = '';
                        this_feed.data_input_show = false;
                    })
            }
        },

        watch: {
            emojis(val) {
                this.data_emojis = val;
            },

            data_emojis(val) {
                this.$emit('update:emojis', val);
            },

            input_show(val) {
                this.data_input_show = val;
            },

            data_input_show(val) {
                this.$emit('update:input_show', val);
            },

            comments(val) {
                this.data_comments = val;
            },

            data_comments(val) {
                this.$emit('update:comments', val);
            }
        }
    });

    Vue.component('emoji-button', {
        template: '#emoji-button',
        props: ['feel']
    });

    Vue.component('emoji-did', {
        template: '#emoji-did'
    });

    Vue.component('comment-button', {
        template: '#comment-button',
        props: ['show_input']
    });

    moment.locale('zh-cn');
    Vue.filter('formatDate', function (value) {
        if (value) {
            return moment(String(value)).fromNow();
        }
    });


    $('#post-new-feed').click(function (e) {
        e.preventDefault();
        $(this).prop('disabled', true);
        var url = $(this).attr('data-confirm');

        if (new_feed.content === '') {
            alert('内容不能为空');
        } else {
            data = {content: new_feed.content};
            $.post(url, data).done(function (data) {
                new_feed.success_message = data['message'];

                new_feed.content = '';
                setTimeout(function () {
                    new_feed.success_message = '';
                }, 2000);

                new_feeds = JSON.parse(data['new_feeds']);
                feeds.feeds = new_feeds.concat(feeds.feeds);
            })
        }
        $(this).prop('disabled', false);
    });

    // 拉取指定页面的feeds
    var load_page_data = function () {
        var options = {
            page: feeds.page,
            type: feeds.type,
            user_id: feeds.user_id
        };

        $.get('/feed/feeds', options)
            .done(function (data) {
                new_feeds = JSON.parse(data['feeds']);
                feeds.request_user_id = data['request_user_id'];
                if (new_feeds.length === 0) {
                    feeds.page = data['page'];
                    loader.status = 3;
                } else {
                    feeds.feeds = feeds.feeds.concat(new_feeds);
                    feeds.page = data['page'];
                    loader.status = 0;
                }

                // console.log('第' + feeds.page + '页拉取完毕');
            })
            .fail(function () {
                loader.status = 2;
            })
    };
    load_page_data();

    // 下拉翻页的处理
    window.onscroll = function (e) {
        var bottomOfWindow = document.documentElement.scrollTop
            + window.innerHeight === document.documentElement.offsetHeight;

        if (bottomOfWindow) {
            loader.load_more_page(e);
        }
    }
});


