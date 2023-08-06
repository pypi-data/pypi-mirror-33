;(function ($) {

    var Comments,
        defaults = {
            initialPage: 1,
            loadMoreBtnSelector: '[data-role="load-more-btn"]',
            listSelector: '[data-role="comment-list"]',
            formSelector: '[data-role="comment-form"]'
        };

    Comments = function (element, options) {
        var $container = $(element),
            options = $.extend({}, defaults, options);

        this.$elements = {
            container: $container,
            loadMoreBtn: $container.find(options.loadMoreBtnSelector),
            list: $container.find(options.listSelector)
        };

        this.urls = options.urls;
        this.page = options.initialPage;
        this.options = options;

        this.setEvents();
        this.$elements.loadMoreBtn.trigger('click');
    };

    Comments.prototype.setEvents = function () {
        var $e = this.$elements;

        $e.loadMoreBtn.on('click', {self: this}, this.loadMore);

        this.getForm().on('submit', {self: this}, this.handleFormSubmit);
    };

    Comments.prototype.loadMore = function (event) {
        var self = event.data.self;

        $.get(self.urls.list, {page: self.page}, function (response) {

            self.$elements.list.append(response.html);

            if (!response['is_next_page_available']) {
                self.$elements.loadMoreBtn.hide();
            }
        });

        self.page += 1;
    };

    Comments.prototype.getForm = function () {
        return this.$elements.container.find(this.options.formSelector);
    };

    Comments.prototype.handleFormSubmit = function (event) {
        event.preventDefault();

        var self = event.data.self,
            $form = self.getForm();

        $.ajax({
            url: self.urls.create,
            method: "POST",
            data: $(this).serialize(),
            success: function (response) {
                self.$elements.list.prepend(response);
                $form.remove();
            },
            error: function (response) {
                $form.replaceWith(response.responseText);
            }
        });
    };

    $.fn.comments = function(options) {
        console.assert(options.urls, 'Option `urls` is required');
        console.assert(options.urls.create, 'Option `urls.create` is required');
        console.assert(options.urls.list, 'Option `urls.list` is required');

        return new Comments(this, options);
    };

}(jQuery));