
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.auto-submit').forEach(select => {
        select.addEventListener('change', function () {
            this.form.submit();
        });
    });
}); 