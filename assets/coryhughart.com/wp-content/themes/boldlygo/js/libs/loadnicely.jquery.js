/**
 * LoadNicely by Ben Foster
 * http://benfoster.io/blog/jquery-loadnicely
 */

(function ($) {

    $.fn.loadNicely = function (options) {

        var defaults = {
            preLoad: function (img) { $(img).hide() },
            onLoad: function (img) { $(img).fadeIn(500); }
        };

        var options = $.extend(defaults, options);

        return this.each(function () {
            if (!this.complete) {
                options.preLoad(this);
                $(this).load(function () { options.onLoad(this); }).attr("src", this.src);
            }
            else {
                options.preLoad(this);
                options.onLoad(this);
            }
        });
    };
})(jQuery);
