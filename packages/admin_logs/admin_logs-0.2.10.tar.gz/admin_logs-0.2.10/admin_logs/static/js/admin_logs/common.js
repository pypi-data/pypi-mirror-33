!function($) {
    $(document).ready(function(){
        $('.admin-logs-collapsed .admin-logs-short, .admin-logs-expanded .admin-logs-short, .admin-logs-collapsed .admin-logs-header, .admin-logs-expanded .admin-logs-header').click(function(){
            var $this = $(this).parents('.admin-logs-entry-parent');
            if ($this.hasClass('admin-logs-collapsed')) {
                $this.addClass('admin-logs-expanded');
                $this.removeClass('admin-logs-collapsed')
            } else {
                $this.addClass('admin-logs-collapsed');
                $this.removeClass('admin-logs-expanded')
            }
            return false;
        });
    });
}(django.jQuery);
