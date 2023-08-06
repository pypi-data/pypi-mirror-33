'use strict';

suite('rb/reviewRequestPage/views/IssueSummaryTable', function () {
    var issueSummaryTableTemplate = _.template('<div id="issue-summary">\n <div class="issue-summary-filters">\n  <select id="issue-reviewer-filter">\n   <option value="all"></option>\n  </select>\n </div>\n <ul>\n  <li class="issue-summary-tab active" data-issue-state="open">\n   <span id="open-counter">2</span>\n  </li>\n  <li class="issue-summary-tab" data-issue-state="resolved">\n   <span id="resolved-counter">3</span>\n  </li>\n  <li class="issue-summary-tab" data-issue-state="dropped">\n   <span id="dropped-counter">1</span>\n  </li>\n  <li class="issue-summary-tab" data-issue-state="all">\n   <span id="total-counter">6</span>\n  </li>\n </ul>\n <table id="issue-summary-table">\n  <thead>\n   <tr>\n    <th class="description-header"></th>\n    <th class="from-header"></th>\n    <th class="last-updated-header"></th>\n   </tr>\n  </thead>\n  <tbody>\n   <tr id="summary-table-entry-1"\n       class="issue resolved hidden"\n       data-issue-id="1"\n       data-reviewer="user1"\n       data-comment-type="diff"\n       data-comment-href="#comment1">\n    <td>\n     <span class="issue-icon rb-icon-issue-resolved"></span>\n     Resolved comment 1\n    </td>\n    <td>user1</td>\n    <td class="last-updated">\n     <time class="timesince" datetime="2017-02-01T20:30:00-07:00">\n      February 1, 2017, 8:30 p.m.\n     </time>\n    </td>\n   </tr>\n   <tr id="summary-table-entry-2"\n       class="issue resolved hidden"\n       data-issue-id="2"\n       data-reviewer="user2"\n       data-comment-type="diff"\n       data-comment-href="#comment2">\n    <td>\n     <span class="issue-icon rb-icon-issue-resolved"></span>\n     Resolved comment 2\n    </td>\n    <td>user2</td>\n    <td class="last-updated">\n     <time class="timesince" datetime="2017-02-02T20:30:00-07:00">\n      February 2, 2017, 8:30 p.m.\n     </time>\n    </td>\n   </tr>\n   <tr id="summary-table-entry-3"\n       class="issue resolved hidden"\n       data-issue-id="3"\n       data-reviewer="user3"\n       data-comment-type="diff"\n       data-comment-href="#comment3">\n    <td>\n     <span class="issue-icon rb-icon-issue-resolved"></span>\n     Resolved comment 3\n    </td>\n    <td>user3</td>\n    <td class="last-updated">\n     <time class="timesince" datetime="2017-02-03T20:30:00-07:00">\n      February 3, 2017, 8:30 p.m.\n     </time>\n    </td>\n   </tr>\n   <tr id="summary-table-entry-4"\n       class="issue open"\n       data-issue-id="4"\n       data-reviewer="user1"\n       data-comment-type="diff"\n       data-comment-href="#comment4">\n    <td>\n     <span class="issue-icon rb-icon-issue-open"></span>\n     Open comment 4\n    </td>\n    <td>user1</td>\n    <td class="last-updated">\n     <time class="timesince" datetime="2017-02-01T20:30:00-07:00">\n      February 1, 2017, 8:30 p.m.\n     </time>\n    </td>\n   </tr>\n   <tr id="summary-table-entry-5"\n       class="issue open"\n       data-issue-id="5"\n       data-reviewer="user2"\n       data-comment-type="diff"\n       data-comment-href="#comment5">\n    <td>\n     <span class="issue-icon rb-icon-issue-open"></span>\n     Open comment 5\n    </td>\n    <td>user2</td>\n    <td class="last-updated">\n     <time class="timesince" datetime="2017-02-02T20:30:00-07:00">\n      February 2, 2017, 8:30 p.m.\n     </time>\n    </td>\n   </tr>\n   <tr id="summary-table-entry-6"\n       class="issue dropped hidden"\n       data-issue-id="6"\n       data-reviewer="user1"\n       data-comment-type="diff"\n       data-comment-href="#comment6">\n    <td>\n     <span class="issue-icon rb-icon-issue-dropped"></span>\n     Dropped comment 6\n    </td>\n    <td>user1</td>\n    <td class="last-updated">\n     <time class="timesince" datetime="2017-02-01T20:30:00-07:00">\n      February 1, 2017, 8:30 p.m.\n     </time>\n    </td>\n   </tr>\n  </tbody>\n </table>\n</div>');
    var view = void 0;

    function getTab(state) {
        return view.$('.issue-summary-tab[data-issue-state="' + state + '"]');
    }

    beforeEach(function () {
        view = new RB.ReviewRequestPage.IssueSummaryTableView({
            el: $(issueSummaryTableTemplate()),
            model: new RB.CommentIssueManager()
        });
        view.$el.appendTo($testsScratch);
    });

    describe('render', function () {
        it('Initial state', function () {
            view.render();

            expect(view.statusFilterState).toBe('open');
            expect(view.reviewerFilterState).toBe('all');
            expect(view.reviewerToSelectorMap).toEqual({
                all: '',
                user1: '[data-reviewer="user1"]',
                user2: '[data-reviewer="user2"]',
                user3: '[data-reviewer="user3"]'
            });

            var $reviewers = view._$reviewerFilter.children();
            expect($reviewers.length).toBe(4);
            expect($reviewers.eq(0).val()).toBe('all');
            expect($reviewers.eq(1).val()).toBe('user1');
            expect($reviewers.eq(2).val()).toBe('user2');
            expect($reviewers.eq(3).val()).toBe('user3');
        });
    });

    describe('Filters', function () {
        describe('Reviewer filter', function () {
            describe('To all', function () {
                it('With issues', function () {
                    view.render();

                    view._$reviewerFilter.val('user1');
                    view._$reviewerFilter.trigger('change');

                    view._$reviewerFilter.val('all');
                    view._$reviewerFilter.trigger('change');

                    var $issues = view.$el.find('.issue').not('.hidden');
                    expect($issues.length).toBe(2);
                    expect($issues.eq(0).data('issue-id')).toBe(4);
                    expect($issues.eq(1).data('issue-id')).toBe(5);
                });

                it('Without issues', function () {
                    view.$el.find('.issue').remove();
                    view.render();

                    view._$reviewerFilter.val('user1');
                    view._$reviewerFilter.trigger('change');

                    view._$reviewerFilter.val('all');
                    view._$reviewerFilter.trigger('change');

                    expect(view.$el.find('.issue').not('.hidden').length).toBe(0);

                    var $noIssues = view.$('.no-issues');
                    expect($noIssues.length).toBe(1);
                });
            });

            describe('To user', function () {
                it('With issues', function () {
                    view.render();
                    view._$reviewerFilter.val('user1');
                    view._$reviewerFilter.trigger('change');

                    var $issues = view.$el.find('.issue').not('.hidden');
                    expect($issues.length).toBe(1);
                    expect($issues.eq(0).data('issue-id')).toBe(4);
                });

                describe('Without issues', function () {
                    function testByUserWithoutIssues(state) {
                        it('And filtered by ' + state + ' issues', function () {
                            view.$el.find('.issue.' + state + '[data-reviewer="user1"]').remove();
                            view.render();

                            view._$reviewerFilter.val('user1');
                            view._$reviewerFilter.trigger('change');

                            var $tab = getTab(state);
                            $tab.click();

                            expect(view.$el.find('.issue').not('.hidden').length).toBe(0);

                            var $noIssues = view.$('.no-issues');
                            expect($noIssues.length).toBe(1);
                            expect($noIssues.text().strip()).toBe('There are no ' + state + ' issues from user1');
                        });
                    }

                    testByUserWithoutIssues('open');
                    testByUserWithoutIssues('resolved');
                    testByUserWithoutIssues('dropped');
                });
            });
        });

        describe('Status filters', function () {
            function testStatusFilters(options) {
                var state = options.state;

                describe(options.description, function () {
                    it('With issues', function () {
                        var expectedIDs = options.expectedIDs;

                        view.render();

                        var $tab = getTab(state);
                        $tab.click();
                        expect($tab.hasClass('active')).toBe(true);

                        var $allIssues = view.$el.find('.issue');
                        var $issues = $allIssues.not('.hidden');

                        expect(view.$el.find('.issue.hidden').length).toBe($allIssues.length - expectedIDs.length);
                        expect($issues.length).toBe(expectedIDs.length);
                        expect(view.$('.no-issues').length).toBe(0);

                        for (var i = 0; i < expectedIDs.length; i++) {
                            expect($issues.eq(i).data('issue-id')).toBe(expectedIDs[i]);
                        }
                    });

                    it('Without issues', function () {
                        var stateSel = view.stateToSelectorMap[state];
                        view.$el.find('.issue' + stateSel).remove();
                        view.render();

                        var $tab = getTab(state);
                        $tab.click();
                        expect($tab.hasClass('active')).toBe(true);

                        expect(view.$el.find('.issue').not('.hidden').length).toBe(0);

                        var $noIssues = view.$('.no-issues');
                        expect($noIssues.length).toBe(1);
                        expect($noIssues.text().strip()).toBe(options.noIssuesText);
                    });
                });
            }

            testStatusFilters({
                description: 'All',
                state: 'all',
                expectedIDs: [1, 2, 3, 4, 5, 6],
                noIssuesText: ''
            });

            testStatusFilters({
                description: 'Open',
                state: 'open',
                expectedIDs: [4, 5],
                noIssuesText: 'There are no open issues'
            });

            testStatusFilters({
                description: 'Resolved',
                state: 'resolved',
                expectedIDs: [1, 2, 3],
                noIssuesText: 'There are no resolved issues'
            });

            testStatusFilters({
                description: 'Dropped',
                state: 'dropped',
                expectedIDs: [6],
                noIssuesText: 'There are no dropped issues'
            });
        });
    });

    describe('Events', function () {
        it('Issue clicked', function () {
            var cb = jasmine.createSpy();

            view.render();
            view.on('issueClicked', cb);

            view.$('.issue[data-issue-id="4"]').click();

            expect(cb).toHaveBeenCalledWith({
                commentType: 'diff',
                commentID: 4,
                commentURL: '#comment4'
            });
        });

        describe('Issue status updated', function () {
            var date = new Date(2017, 7, 6, 1, 4, 30);
            var $issue = void 0;
            var $icon = void 0;
            var comment = void 0;

            beforeEach(function () {
                comment = new RB.DiffComment({
                    id: 4
                });

                view.render();
                expect(view.$('#resolved-counter').text()).toBe('3');
                expect(view.$('#open-counter').text()).toBe('2');
                expect(view.$('#dropped-counter').text()).toBe('1');
                expect(view.$('#total-counter').text()).toBe('6');

                $issue = view.$('.issue[data-issue-id="4"]');
                $icon = $issue.find('.issue-icon');
            });

            it('To dropped', function () {
                comment.set('issueStatus', 'dropped');
                view.model.trigger('issueStatusUpdated', comment, 'open', date);

                expect(view.$('#open-counter').text()).toBe('1');
                expect(view.$('#dropped-counter').text()).toBe('2');
                expect(view.$('#total-counter').text()).toBe('6');

                expect($icon.hasClass('rb-icon-issue-open')).toBe(false);
                expect($icon.hasClass('rb-icon-issue-dropped')).toBe(true);
            });

            it('To resolved', function () {
                comment.set('issueStatus', 'resolved');
                view.model.trigger('issueStatusUpdated', comment, 'open', date);

                expect(view.$('#resolved-counter').text()).toBe('4');
                expect(view.$('#open-counter').text()).toBe('1');
                expect(view.$('#total-counter').text()).toBe('6');

                expect($icon.hasClass('rb-icon-issue-open')).toBe(false);
                expect($icon.hasClass('rb-icon-issue-resolved')).toBe(true);
            });

            it('To open', function () {
                comment.set({
                    issueStatus: 'open',
                    id: 1
                });
                view.model.trigger('issueStatusUpdated', comment, 'resolved', date);

                $issue = view.$('.issue[data-issue-id="1"]');
                $icon = $issue.find('.issue-icon');

                expect(view.$('#resolved-counter').text()).toBe('2');
                expect(view.$('#open-counter').text()).toBe('3');
                expect(view.$('#total-counter').text()).toBe('6');

                expect($icon.hasClass('rb-icon-issue-resolved')).toBe(false);
                expect($icon.hasClass('rb-icon-issue-open')).toBe(true);
            });

            it('After re-renders', function () {
                view.render();
                view.render();

                comment.set('issueStatus', 'resolved');
                view.model.trigger('issueStatusUpdated', comment, 'open', date);

                expect(view.$('#resolved-counter').text()).toBe('4');
                expect(view.$('#open-counter').text()).toBe('1');
                expect(view.$('#total-counter').text()).toBe('6');

                expect($icon.hasClass('rb-icon-issue-open')).toBe(false);
                expect($icon.hasClass('rb-icon-issue-resolved')).toBe(true);
            });

            afterEach(function () {
                expect($issue.find('.last-updated time').attr('datetime')).toBe(date.toISOString());
            });
        });

        describe('Header clicked', function () {
            function testHeaderSorting(options) {
                it(options.description, function () {
                    view.render();

                    var event = $.Event('click');
                    event.shiftKey = !!options.shiftKey;
                    view.$(options.headerSel).trigger(event);

                    var $issues = view.$('.issue');
                    expect($issues.length).toBe(6);

                    var expectedIDs = options.expectedIDs;

                    for (var i = 0; i < expectedIDs.length; i++) {
                        expect($issues.eq(i).data('issue-id')).toBe(expectedIDs[i]);
                    }
                });
            }

            describe('Ascending', function () {
                testHeaderSorting({
                    description: 'Description',
                    headerSel: '.description-header',
                    expectedIDs: [6, 4, 5, 1, 2, 3]
                });

                testHeaderSorting({
                    description: 'From',
                    headerSel: '.from-header',
                    expectedIDs: [1, 4, 6, 2, 5, 3]
                });

                testHeaderSorting({
                    description: 'Last Updated',
                    headerSel: '.last-updated-header',
                    expectedIDs: [3, 2, 5, 1, 4, 6]
                });
            });

            describe('Descending', function () {
                testHeaderSorting({
                    description: 'Description',
                    headerSel: '.description-header',
                    expectedIDs: [3, 2, 1, 5, 4, 6],
                    shiftKey: true
                });

                testHeaderSorting({
                    description: 'From',
                    headerSel: '.from-header',
                    expectedIDs: [3, 2, 5, 1, 4, 6],
                    shiftKey: true
                });

                testHeaderSorting({
                    description: 'Last Updated',
                    headerSel: '.last-updated-header',
                    expectedIDs: [1, 4, 6, 2, 5, 3],
                    shiftKey: true
                });
            });
        });
    });
});

//# sourceMappingURL=issueSummaryTableViewTests.js.map