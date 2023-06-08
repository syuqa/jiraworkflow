var routes = [
    {
      path: '/index/',
      url: './profile',
      ignoreCache: true,
      reloadCurrent: true,
      reloadAll: true,
      on: {
        pageInit: function (event, page) {
            page.$el.on('smartselect:opened', '.filter-global', function(){
                popup = $$('.popup[data-select-name="filter"] .page-content')
                console.log(popup.addClass('simple'))
            })
          //  
          app.toggle.create({
            el: '.jira-flter',
            on: {
              change: function (el) {
                console.log(el.checked)
                if (el.checked) {
                    // do something
                        $$('.filter-custom').css('display', '')
                        $$('.filter-global').css('display', 'none')
                    }else{
                        $$('.filter-custom').css('display', 'none')
                        $$('.filter-global').css('display', '')
                    }
              }
            }
            });

            app.toggle.create({
                el: '.jira-task',
                on: {
                    change: function(el){
                        if (el.checked) {
                        // do something
                            $$('.task-week-custom').css('display', '')
                            $$('.task-week-global').css('display', 'none')

                            $$('.task-time-custom').css('display', '')
                            $$('.task-time-global').css('display', 'none')
                        }else{
                            $$('.task-week-custom').css('display', 'none')
                            $$('.task-week-global').css('display', '')

                            $$('.task-time-custom').css('display', 'none')
                            $$('.task-time-global').css('display', '')
                        }
                    }
                }
            })
          //
          var monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
                calendarInline = app.calendar.create({
                    containerEl: '#demo-calendar-inline-container',
                    value: [new Date()],
                    weekHeader: false,
                    renderToolbar: function () {
                    return `
                    <div class="toolbar calendar-custom-toolbar no-shadow">
                        <div class="toolbar-inner">
                        <div class="left">
                            <a href="#" class="link icon-only"><i class="icon icon-back ${app.theme === 'md' ? 'color-black' : ''}"></i></a>
                        </div>
                        <div class="center"></div>
                        <div class="right">
                            <a href="#" class="link icon-only"><i class="icon icon-forward ${app.theme === 'md' ? 'color-black' : ''}"></i></a>
                        </div>
                        </div>
                    </div>
                    `;
                    },
                    on: {
                        init: function (c) {
                                $$('.calendar-custom-toolbar .center').text(monthNames[c.currentMonth] + ', ' + c.currentYear);
                                $$('.calendar-custom-toolbar .left .link').on('click', function () {
                                    calendarInline.prevMonth();
                                });
                                $$('.calendar-custom-toolbar .right .link').on('click', function () {
                                    calendarInline.nextMonth();
                                });
                            },
                        monthYearChangeStart: function (c) {
                                $$('.calendar-custom-toolbar .center').text(monthNames[c.currentMonth] + ', ' + c.currentYear);
                            },
                        calendarChange: function(c){
                          
                        },
                        dayClick: function(c){
                            },
                        
                    }
                });
        }
      }
    },
  ]