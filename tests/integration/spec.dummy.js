describe('Protractor Demo App', function() {
    it('should have a title', function() {
        browser.get('http://www.django-cms.org');

        expect(browser.getTitle()).toEqual('The easiest way to build and manage your Django projects - django-cms.org');
    });
});
