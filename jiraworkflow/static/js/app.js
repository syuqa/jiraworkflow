var $$ = Dom7;

function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

function saved(){
  app.toast.create({
    icon: '<i class="material-icons">task_alt</i>',
    text: 'Сохранено',
    position: 'center',
    closeTimeout: 2000,
  }).open()
}

function popup_info(el){
  console.log(el.find('.popup-sync-status'))

  el.on('popup:closed', '.popup-sync-status', function (e, popup) {
    app.popup.destroy('.popup')
  })
  
  el.on('popup:open','.popup-sync-status', function (e) {
    
    console.log(e)
    let status = $(e.target).find('input[name="task-status"]')
  
    if ($(e.target).find(".jsoneditor").length == 0){
      var container = $(e.target).find("#id_json")[0];
      var textarea = $(e.target).find("#id_json_textarea");
  
      var options = {"mode": "code", "sort": false, "search": false, "readOnly": true, "disable_properties": true};
      var editor = new JSONEditor(container, options);
      app.editor = editor
      var json = textarea.val();
      editor.set(JSON.parse(json));
    }
  
    // Только чтение
    $(e.target).find(".ace_text-input").prop('readonly', true);
  
    // Дабавляем кнопку закрыть
    let close = $(e.target).find(".jsoneditor-poweredBy")
        close.replaceWith('<a class="jsoneditor-poweredBy popup-close">Закрыть</a>')
    
    // Цвет рамки взависимости от статуса
    let title = $$(e.target).find(".jsoneditor-menu")
    let jedit = $$(e.target).find(".jsoneditor")
  
    if (status.val() == 'SUCCESS'){  
      title.css('background', 'green')
      title.css('border-bottom', '1px solid green')
      jedit.css('border', 'thin solid green')
    }else if (status.val() == 'FAILURE'){
      title.css('background', 'crimson')
      title.css('border-bottom', '1px solid crimson')
      jedit.css('border', 'thin solid crimson')
    }
  });
}


// Профиль
routes.push({
  path: '/profile/',
  url: './profile',
  on: {
    pageInit: function(event, page){}
  }
})

// Разлогин
routes.push({
  path: '/loginout/',
  url: './accounts/login/out'
})


// Выборочная синхронизация
routes.push({
  path: '/custom-sync/',
  url: './users/synchronization/custom', 
  on: {
    pageInit: function(event, page){
      // Запуск синхронизации
      page.$el.on('click', '.button-run-sync', function(){
        let type_sync = page.$el.find('.buttons-sync .segmented .button-active').attr('name')
        let nwl = new Object()
        var tasks = JSON.parse($('.full-task-list').text())
        let miting = page.$el.find('input[name="mitings"]').is(':checked')
        $('.data-table td.checkbox-cell input:checked').map((i, el) => {
          let data = $(`#week_${el.id}, #project_${el.id}, #task_${el.id}, #date_${el.id}, #time_${el.id}`).
              map((i, el) => {return el.textContent})
              let week = data[0]
              let project = data[1]
              let task = data[2]
              let date = data[3]
              let time = data[4]
              if (nwl.hasOwnProperty(week)){
                if (nwl[week].hasOwnProperty(project)){
                  if (nwl[week][project].hasOwnProperty(task)){
                        if (nwl[week][project][task].hasOwnProperty('worklog')){
                            nwl[week][project][task]['worklog'][date] = time
                        }
                  }else{
                    let info = tasks[week][project][task]
                        info['worklog'] = {[date]: time}
                      nwl[week][project][task] = info
                  }
                }else{
                  let info = tasks[week][project][task]
                      info['worklog'] = {[date]: time}
                  nwl[week][project] = {[task]: info}
                }
              }else{
              let info = tasks[week][project][task]
                  info['worklog'] = {[date]: time}
              nwl[week] = {[project]: {[task]: info}}
          }
        })
        app.request.setup({
          headers: {
            "X-CSRFToken": getCookie('csrftoken')
          }
          })
        app.request.postJSON('users/synchronization/custom/sync', {task: nwl, metrhod: type_sync, miting: miting, dates:app.calendarInline.getValue()}, function(request){
          console.log(request)
          // 
          app.notification.create({
            title: 'Синхронизация',
            titleRightText: 'Задание',
            subtitle: 'Синхронизация запущена',
            text: 'Результаты выполнения вожно увидить в списке задач, на странице пользователя.',
            closeTimeout: 3000,
          }).open()
          //
          navigate('/profile/')
          //
        }, function(request){
          console.log(request)

         let nw = app.notification.create({
            title: 'Синхронизация',
            titleRightText: `${request.status}: ${request.statusText}`,
            subtitle: 'Ошибка при запуске задания',
            closeButton: true,
            on: {
              open: function () {
               let detail = this.$el.find('.notification-content')
                   detail.append(
                      $$(`<div style="padding-top: 5px;">
                            <a href="#" style="color: darkblue;border-width: 0px 0px 1px 0px;border-style: double;" class="popup-open" data-popup=".popup-sync-error">Показать детали</a>
                            <div class="popup popup-sync-status popup-sync-error">
                              <div class="view">
                                <div class="page">
                                  <div class="page-content">
                                    <input style="display: none;" type="text" name="task-status" value="FAILURE" />
                                    <div style="height:100%;width:100%;display:inline-block;" required="" id="id_json" class=""></div>
                                    <textarea id="id_json_textarea" name="json" required="" style="display: none" >
                                    {
                                      "request": {"code": "${request.status}", "status": "${request.statusText}"},
                                      "response": ${request.response}
                                    }
                                    </textarea>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>`)
                      )
                    this.$el.on('click', '.popup-open', function(){
                      nw.close()
                    })
              }
            }
          }).open()
        }, 'json')
        console.log(nwl, type_sync)
      })

      // выбор типа синхронизации
      page.$el.on('click', '.buttons-sync .segmented button', function(){
        page.$el.find('.buttons-sync .segmented button').removeClass('button-active')
        $(this).addClass('button-active')
      })

      // Разблокировка синхронизации
      $(document).on('click', '.data-table input[type="checkbox"]', function(){
        if (! app.dataTable.get('.data-table')){
          app.dataTable.create({el: '.data-table'})
        }

        let bs = page.$el.find('.buttons-sync')
        let bl = page.$el.find('.button-load')
        if (page.$el.find('.data-table input[type="checkbox"]:checked').length > 0){
            if (bs.hasClass('simple')){
              bs.removeClass('simple')
            }
            if (! bl.hasClass('simple')){
              bl.addClass('simple')
            }
        }else{
          if (! bs.hasClass('simple')){
            bs.addClass('simple')
          }
          if (bl.hasClass('simple')){
            bl.removeClass('simple')
          }
        }
      })
      function sync(filters, mitings, custom_dates=false, dates=undefined){
        let errmesage = (message) => {
          return `
          <div style="background: url('/static/img/cloud_sync.webp') no-repeat;width: 400px;height: 400px;background-size: 100%;margin: auto;"></div>
          <font class="start-info" style="width: 100%;text-align: center;display: block;">${message}</font>
          <div class="process-load" style="display: none;">
            <p style="margin: auto;text-align: center;" class="">Загружаю, подождите</p>
            <p><span style="width: 100px;margin: auto;" id="inline-progressbar" class="progressbar-infinite color-multi"></span></p>
          </div>
          `
        }
        const datestring = (d) => {return d.getFullYear() + "/" + (d.getMonth()+1) + "/" + d.getDate()}
          page.$el.find('.process-load').css('display', '')
          page.$el.find('.start-info').css('display', 'none')
          if (custom_dates){
            app.request.get(`./users/synchronization/custom/tasks?filters=${filters}&sdate=${datestring(dates[0])}&edate=${datestring(dates[1])}&mitings=${mitings}`, function(request){
            page.$el.find('.block-task-list').html(request)
            page.$el.on('click', '.project-not-fount', function(){
              app.dialog.confirm('Отстутвует информация о проете. Перейти в профиль Timetta ?', function () {
                navigate('/timetta/')
            });
          })
            popup_info($(document))
            }, function(request){
              console.log(request)
              //page.$el.find('.block-task-list').html(errmesage(request))
            })
          }else{
            app.request.get(`./users/synchronization/custom/tasks?filters=${filters}&mitings=${mitings}`, function(request){
              page.$el.find('.block-task-list').html(request)
              page.$el.on('click', '.project-not-fount', function(){
                app.dialog.confirm('Отстутвует информация о проете. Перейти в профиль Timetta ?', function () {
                  navigate('/timetta/')
              });
            })
            }, function(request){
              console.log(request)
              //page.$el.find('.block-task-list').html(errmesage(request))
            })
            popup_info($(document))
          }
         
      }

      var monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
      var calendarInline = app.calendar.create({
          containerEl: '#demo-calendar-inline-container',
          value: [new Date()],
          weekHeader: false,
          rangePicker: true,
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
                      $('.calendar-custom-toolbar .center').text(monthNames[c.currentMonth] + ', ' + c.currentYear);
                      $('.calendar-custom-toolbar .left .link').on('click', function () {
                          calendarInline.prevMonth();
                      });
                      $('.calendar-custom-toolbar .right .link').on('click', function () {
                          calendarInline.nextMonth();
                      });
                  },
              monthYearChangeStart: function (c) {
                      $('.calendar-custom-toolbar .center').text(monthNames[c.currentMonth] + ', ' + c.currentYear);
                  },
              calendarChange: function(c){
                  if (c.params.rangePicker) {
                      if (c.value.length > 1){
                      }
                  }else{
                  }
              },
              dayClick: function(c){
                  },
              
          }
      });
      app.calendarInline = calendarInline
      
      page.$el.on('smartselect:closed', '.smart-select', function(event, el){
        let is_date_input = false
        Array.from(app.smartSelect.get('.smart-select-filter').selectEl.selectedOptions).forEach(el => {
          if (el.className == 'is-date-input'){
              console.log(el.className);
              is_date_input = true
            }
          })
        let $calendar_el = page.$el.find('.card-calendar')
        if (is_date_input){  
          if ($calendar_el.hasClass("simple")){
              $calendar_el.removeClass("simple")
          }
        }else{
          if (! $calendar_el.hasClass("simple")){
                $calendar_el.addClass("simple")
          }
        }
      })

      page.$el.on('click', '.button-load', function(){
        let dates = app.calendarInline.getValue()
        let filters = app.smartSelect.get('.smart-select-filter')
        let mitings = page.$el.find('input[name="mitings"]').is(':checked')
        if (filters.getValue().length > 0){
            if (! page.$el.find('.card-calendar').hasClass('simple')){
                if (dates.length > 1){
                    sync(filters.getValue(), mitings, true, dates)
                }else{
                  app.notification.create({
                    title: 'Синхронизация',
                    titleRightText: 'ошибка',
                    subtitle: 'Произошла ошибка',
                    text: 'Выбирете диапазон дат в календаре',
                    closeTimeout: 3000,
                  }).open()
                }                  
            }else{
              sync(filters.getValue(), mitings)
            }
        }else{
          app.notification.create({
            title: 'Синхронизация',
            titleRightText: 'ошибка',
            subtitle: 'Произошла ошибка',
            text: 'Выбирете хотябы один фильтр',
            closeTimeout: 3000,
          }).open()
        }
      })
    }
  }

})

// Radis task list
routes.push({
  path: '/worklog/:task/:backpage',
  content: `
      <div class="page">
        <div class="navbar">
          <div class="navbar-bg"></div>
          <div class="navbar-inner">
            <div class="left">
                  <a class="link">
                      <img width="100px" src="/static/img/redis.png"  />
                  </a>
                </div>
            <div class="title" style="text-align: center;">Информация о синхронизации</div>
            <div class="right">
                <a href="/jira/" class="material-icons link">close</a>
            </div>
          </div>
        </div>
            
        <!-- Контент -->
        <div class="page-content"></div>
                              
      </div>
  `,
  on: {
    pageInit: function(event, page){

      let task = page.route.params.task
      let backpage = page.route.params.backpage
      
      page.$el.find('.right a').attr('href', `/${backpage}/`)
      
      app.request.get(`./jira/worklog/${task}`, function(request){
        page.$el.find('.page-content').html(request)
        page.$el.on('click', '.list-users li a', function(){
          let user = $(this).attr('user')
          // color
          page.$el.find('.list li').css('background', '')
          page.$el.find(`.list-users li[user="${user}"]`).css('background', 'beige')
          // display
          page.$el.find(`.list-weeks li`).css('display', 'none')
          page.$el.find(`.list-tasks li`).css('display', 'none')
          page.$el.find(`.list-weeks li[user="${user}"]`).css('display', 'block')
        })

        page.$el.on('click', '.list-weeks li a', function(){
          let user = $(this).attr('user')
          let week = $(this).attr('week')
          // color 
          page.$el.find('.list-weeks li').css('background', '')
          page.$el.find(`.list-weeks li[user="${user}"][week="${week}"]`).css('background', 'beige')
          // display
          page.$el.find(`.list-tasks li`).css('display', 'none')
          page.$el.find(`.list-tasks li[user="${user}"][week="${week}"]`).css('display', 'block')
        })
        console.log('popup action init')
        popup_info(page.$el)
        //        
      })
    }
  }
})

// Tиметта
routes.push({
  path: '/timetta/',
  url: './timetta',
  on: {
    pageInit: function(event, page){

      page.$el.on('formajax:success', '.jira-account', function() {
        let rederect = $(this).attr('redirect')
        //
        app.toast.create({
          icon: '<i class="material-icons">task_alt</i>',
          text: 'Сохранено',
          position: 'center',
          closeTimeout: 2000,
        }).open() 
        //
        if (rederect){
          navigate(rederect)
        }
      })
      
      var dialog_create = (content) => {
        var dialog = app.dialog.create({
        title: 'Проект',
        content: content,
        cssClass: 'dialog-project',
        on: {
          opened: function (dialog) {
            dialog.$el.on('click', '.project-resurse', function(){
              console.log(this)
              let sort = $$(this)
              if (sort.attr('enable') == "false"){
                dialog.$el.find('.get-task-list[my_resurse="false"]').css('display', 'none')
                sort.attr('enable', 'true')
              }else{
                dialog.$el.find('.get-task-list[my_resurse="false"]').css('display', '')
                sort.attr('enable', 'false')
              }
            })

            app.tooltip.create({
              targetEl: '.tooltip-mitting-summary',
              text: `
              <h3>Заголовок события в Я.Календаре</h3>
                <p>Поддерживает следующие форматы:</p>
              <ol>
                <li>Заголовоки целеком через точку с запятой - ";"</li>
                <li>Ключивые слова, через запяту ","</li>
                <li>Кортеж ключевых слов, через ";"</li>
              </ol>
              <h3>Примеры</h3>
              <ol>
                  <li><i>Встерча по проекту SMPL;Статус по проету SMPL</i></li>
                  <li><i>встреча,smpl</i></li>
                  <li><i>встреча,smpl;статус,smpl</i></li>
              </ol>
              `
            })
            

            jQuery('#project_list').mCustomScrollbar({advanced:{ updateOnSelectorChange: "li", autoScrollOnFocus: "ul li", updateOnContentResize:true}})
            jQuery('#task_list').mCustomScrollbar({advanced:{ updateOnSelectorChange: "li", autoScrollOnFocus: "ul li" , updateOnContentResize:true}})

            dialog.$el.find('input').change()
            dialog.$el.find('textarea').change()
            dialog.$el.on('formajax:success', '.form-ajax-submit', function() {
            dialog.close()
            $$('.dialog').remove()
            let rederect = $(this).attr('rederect')
            if (rederect){
                navigate(rederect)
              }
            });

            // закрыть
            dialog.$el.on('click', 'button.close', function(){
              dialog.close()
              $('.dialog').remove()
            })

            // 
            dialog.$el.on('click', '.get-task-list', function(){
              let project = $$(this).attr('project')
              let $meeting_task_el = dialog.$el.find("#id_meeting_task_id")
              let $task_el = dialog.$el.find("#id_task_id")
                  $task_el.val('')
                  $meeting_task_el.val('')
                  $meeting_task_el.change()
                  $task_el.change()
              dialog.$el.find('.get-task-list').css('background', '')
              $$(this).css('background', 'aliceblue')
              let $proj_el = dialog.$el.find("#id_project_id")
                  $proj_el.val(project)
                  $proj_el.change()
              app.request.get(`./timetta/tasks/${project}`, function(request){
                let list = dialog.$el.find('.task-list ul')
                    list.html(request)
              })
            })

            dialog.$el.on('click', '.timetta_task_id', function(){
              console.log(this.id)
              app.project_mode_input = this.id
              dialog.$el.find(`input[type="radio"]`).prop('checked', false)
              if (this.value.length > 0){
                jQuery('#task_list').mCustomScrollbar('scrollTo', `li[task="${this.value}"]`);
                let $el_task = dialog.$el.find(`input[value="${this.value}"][type="radio"]`)
                    $el_task.prop('checked', true);
              }
            })

            dialog.$el.on('change', 'input[name="project-task"]', function(){
            let $el = dialog.$el.find(`#${app.project_mode_input || 'id_task_id'}`)
                $el.val(this.value)
                $el.change()
            })

          
          let data = dialog.$el.find('#id_jira_tag, #id_project_id, #id_task_id')
          console.log(data)
          if (data.length == 3){
            let project = data[1].value
            let task = data[2].value
            let $el_projrct = dialog.$el.find(`.get-task-list[project="${project}"]`)
                $el_projrct.css('background', 'aliceblue')
                jQuery('#project_list').mCustomScrollbar('scrollTo',`.get-task-list[project="${project}"]`);
                app.request.get(`./timetta/tasks/${project}`, function(request){
                  let list = dialog.$el.find('.task-list ul')
                      list.html(request)
                      let $el_task = dialog.$el.find(`input[value="${task}"][type="radio"]`)
                          $el_task.prop('checked', true);
                          jQuery('#task_list').mCustomScrollbar('scrollTo', `li[task="${task}"]`);
                          
                })
          }
          }
        }
      })
      
      dialog.open()
      }
      //
      var dialog_edit_simple = (content) => {
        var dialog = app.dialog.create({
        title: 'Фильтр задач Jira',
        content: content,
        cssClass: 'dialog-filters',
        on: {
          opened: function (dialog) {

            
            dialog.$el.find('input').change()
            dialog.$el.find('textarea').change()
            $('.form-ajax-submit').on('formajax:success', function() {
              dialog.close()
              $$('.dialog').remove()
              let rederect = $(this).attr('rederect')
              if (rederect){
                navigate(rederect)
              }
            });

            // close
            dialog.$el.on('click', 'button.close', function(){
              dialog.close()
              $$('.dialog').remove()
            })

            // totip
            dialog.$el.find('.dialog-title').append('<i class="icon material-icons tooltip-jinja" style="float: right">help</i>')
            app.tooltip.create({
              targetEl: '.tooltip-jinja',
              text: `
              <h3>Информация о задаче</h3>
              <ul>
                <li><b>issue</b> - Индификатор задачи</li>
                <li><b>issue_summary</b> - Заголовок/краткое содержание задачи</li>
                <li><b>issue_link</b> - Ссылка на задачу</li>
                <li><b>issue_status</b> - Статус задачи</li>
              </ul>

              <h3>Пример</h3>
              <p>{{issue}}: {{ issue_link }}</p>

              <h3>Результат</h3>
              <p>TEST-101: https://jira.simple.com/browse/TEST-101</p>
              `
            });

          }
        }
      })
      dialog.open()
      }
      //
      // Редактировать шаблон
      page.$el.on('click', '.edit-simple', function(){
        console.log('create')
        app.request.get('./timetta/simple', function(request){
          dialog_edit_simple(request)
        })
      })

      // Новый проект
      page.$el.on('click', '.create-project', function(){
        console.log('create')
        app.request.get('./timetta/projects/0', function(request){
          dialog_create(request)
        })
      })

      // Редактировать проект
      page.$el.on('click', '.edit-project', function(){
        let id = $(this).attr('index') 
        app.request.get(`./timetta/projects/${id}`, function(request){
          dialog_create(request)
        })
      })

      // следующих 3
      page.$el.on('click', '.action-filter-list .next', function(){
        let current = parseInt(page.$el.find('.filter-list').attr('page'))
        let li = page.$el.find('.filter-list li')
        console.log(current, li)
        if (li.length > current * 3){
          li.forEach(element => {
            let index = parseInt($(element).attr('index')) + 1
            console.log(index, current, current *3, current * 3 + 3)
            if (index > current * 3 && index <= current * 3 + 3){
              $$(element).css('display', '')
            }else{
              $$(element).css('display', 'none')
            }
          });
          page.$el.find('.action-filter-list .in').text(current + 1)
          page.$el.find('.filter-list').attr('page', current + 1)
        }
        
      })

      // предедущих 3
      page.$el.on('click', '.action-filter-list .back', function(){
        let current = parseInt(page.$el.find('.filter-list').attr('page'))
        let li = page.$el.find('.filter-list li')
        console.log(current, li)
        if (current > 1){
          li.forEach(element => {
            let index = parseInt($(element).attr('index')) + 1
            console.log(index, current, (current -1) * 3, (current -1) * 3 - 3)
            if (index <= (current -1) * 3 && index > (current -1) * 3 - 3){
              $$(element).css('display', '')
            }else{
              $$(element).css('display', 'none')
            }
          });
          page.$el.find('.action-filter-list .in').text(current - 1)
          page.$el.find('.filter-list').attr('page', current - 1)
        }
        
      })
}
    
  }
})

// Пользователи
routes.push({
  path: '/users/',
  url: './users',
  on: {
    pageInit: function(event, page) {

        //
        var dialog_create = (content) => {
          var dialog = app.dialog.create({
          title: 'Пользователь',
          content: content,
          cssClass: 'dialog-user',
          on: {
            opened: function (dialog) {
              dialog.$el.find('input').change()
              dialog.$el.find('textarea').change()
              dialog.$el.on('formajax:success', '.form-ajax-submit', function() {
              dialog.close()
              $('.dialog').remove()
              let rederect = $(this).attr('rederect')
              if (rederect){
                  navigate(rederect)
                }
              });

              // закрыть
              dialog.$el.on('click', 'button.close', function(){
                dialog.close()
                $$('.dialog').remove()
              })
            }
          }
        })
        
        dialog.open()
        }
      
      // Новый пользователь
      page.$el.on('click', '.add-user', function(){
        app.request.get('./users/form/0', function(request){
          dialog_create(request)
        })
      })

      // Изменить данные пользователя
      page.$el.on('click', '.user-edit', function(){
        let id = $(this).attr('index') 
        app.request.get(`./users/form/${id}`, function(request){
         dialog_create(request)
       })
     })

     // Удалить пользователя
     page.$el.on('click', '.user-remove', function(){
      let users = page.$el.find('table td.checkbox-cell input:checked').map(el => { return $(el).attr('index')})
      if (users.length > 0){
        app.request.setup({
          headers: {
            "X-CSRFToken": getCookie('csrftoken')
          }
        })
        app.request.postJSON('./users/delete', {users: users}, 
        function(request){
          console.log(e)
          navigate('/users/')
        },
        function(request){
          console.log(request)
        }
        )
      }
    })

    }
  }
})

// Конфигурации Jira
routes.push({
  path: '/jira/',
  url: './jira',
  ignoreCache: true,
  reloadCurrent: true,
  reloadAll: true,
  on: {
    pageInit: function (event, page) {
      // refresh
      page.$el.on('click', '.refresh', function(){
        let page = $$(this).attr('page')
        console.log('reload', page)
        navigate(page)
      });
      // Принудительный запуск синхронизации
      page.$el.on('click', '.run-sync', function () {
        app.dialog.confirm('Запустить выполнение задания?', 'Запуск задания', function () {
          app.request.get(`./jira/sync`, function(request){
            app.toast.create({
              icon: '<i class="material-icons">play_circle_outline</i>',
              text: 'Задание запущено',
              position: 'center',
              closeTimeout: 2000,
            }).open()
          }, function(request){
              console.log(request)
              var notificationWithButton = app.notification.create({
                title: 'Ошибка запуска задачи',
                subtitle: `${request.status} ${request.statusText}`,
                closeButton: true,
              });
              notificationWithButton.open()
          })
        });
      });

      // cохранение аккаунта jira
      $$('.jira-account').on('formajax:success', function() {
        let rederect = $(this).attr('redirect')

        app.toast.create({
          icon: '<i class="material-icons">task_alt</i>',
          text: 'Сохранено',
          position: 'center',
          closeTimeout: 2000,
        }).open()
        
        if (rederect){
          navigate(rederect)
        }
      });

      $$('.jira-exercise').on('formajax:success', function() {
        let rederect = $(this).attr('redirect')

        app.toast.create({
          icon: '<i class="material-icons">task_alt</i>',
          text: 'Сохранено',
          position: 'center',
          closeTimeout: 2000,
        }).open()

        if (rederect){
          navigate(rederect)
        }
      })

      // следующих 3
      page.$el.on('click', '.action-filter-list .next', function(){
        let current = parseInt(page.$el.find('.filter-list').attr('page'))
        let li = page.$el.find('.filter-list li')
        console.log(current, li)
        if (li.length > current * 3){
          li.forEach(element => {
            let index = parseInt($(element).attr('index')) + 1
            console.log(index, current, current *3, current * 3 + 3)
            if (index > current * 3 && index <= current * 3 + 3){
              $$(element).css('display', '')
            }else{
              $$(element).css('display', 'none')
            }
          });
          page.$el.find('.action-filter-list .in').text(current + 1)
          page.$el.find('.filter-list').attr('page', current + 1)
        }
        
      })
      // предедущих 3
      page.$el.on('click', '.action-filter-list .back', function(){
        let current =  parseInt(page.$el.find('.filter-list').attr('page'))
        let li = page.$el.find('.filter-list li')
        console.log(current, li)
        if (current > 1){
          li.forEach(element => {
            let index = parseInt($(element).attr('index')) + 1
            console.log(index, current, (current -1) * 3, (current -1) * 3 - 3)
            if (index <= (current -1) * 3 && index > (current -1) * 3 - 3){
              $$(element).css('display', '')
            }else{
              $$(element).css('display', 'none')
            }
          });
          page.$el.find('.action-filter-list .in').text(current - 1)
          page.$el.find('.filter-list').attr('page', current - 1)
        }
        
      })
      // Create filter
      var dialog_create_filter = (content) => {
        var dialog = app.dialog.create({
        title: 'Фильтр задач Jira',
        content: content,
        cssClass: 'dialog-filters',
        on: {
          /*
          open: function (sheet) {
            console.log('Sheet open');
            var code = CodeMirror.fromTextArea(sheet.$el.find('textarea')[0], 
            { 
              mode: 'text/x-sql', 
              lineNumbers: true, 
              fullScreen: false,
              extraKeys: {"Alt-F": "findPersistent"}
            })
            
            sheet.$el.on('click', '.autoformat', function(){
              var range = getSelectedRange();
              code.autoFormatRange(range.from, range.to);
            })

            sheet.$el.on('click', '.search', function(){
              CodeMirror.commands.findPrev(code)
            })

            sheet.$el.on('click', '.replace-all', function(){
              CodeMirror.commands.replaceAll(code)
            })

            // Выделить все
            //CodeMirror.commands["selectAll"](code);
            
            function getSelectedRange() {
              return { from: code.getCursor(true), to: code.getCursor(false) };
            }
            
            sheet.code = code

          }, */
          opened: function (dialog) {

            
            dialog.$el.find('input').change()
            dialog.$el.find('textarea').change()
            $('.form-ajax-submit').on('formajax:success', function() {
              dialog.close()
              $$('.dialog').remove()
              let rederect = $(this).attr('rederect')
              if (rederect){
                navigate(rederect)
              }
            });

            // close
            dialog.$el.on('click', 'button.close', function(){
              dialog.close()
              $$('.dialog').remove()
            })

            // totip
            dialog.$el.find('.dialog-title').append('<i class="icon material-icons tooltip-jinja" style="float: right">help</i>')
            app.tooltip.create({
              targetEl: '.tooltip-jinja',
              text: `
              <h3>Даты</h3>
              <ul>
                <li><b>current_week_day_monday</b> - Понедельник текущей недели</li>
                <li><b>current_week_day_tuesday</b> - Вторник текущей недели</li>
                <li><b>current_week_day_wednesday</b> - Среда текущей недели</li>
                <li><b>current_week_day_thursday</b> - Четверг текущей недели</li>
                <li><b>current_week_day_friday</b> - Пятница текущей недели</li>
                <li><b>current_week_day_saturday</b> - Суббота текущей недели</li>
                <li><b>current_week_day_sunday</b> - Воскресенье текущей недели</li>
              </ul>

              <h3>Данные пользователя</h3>
              <ul>
                <li><b>username</b> - Имя пользователя</li>
                <li><b>ursremail</b> - Email пользователя</li>
              </ul>  


              <h3>Пример</h3>
              <p>worklogAuthor = {{username}}</p>
              <p style="padding-left: 20px;padding-top: 0px;padding-button: 0px">and worklogDate >= '{{current_week_day_monday}}'</p> 
              <p style="padding-left: 20px;padding-top: 0px;padding-button: 0px">and worklogDate <= '{{current_week_day_sunday}}'</p>
              <p style="padding-left: 20px;padding-top: 0px;padding-button: 0px">order by created DESC</p>
              `
            });

          }
        }
      })
      dialog.open()
      }
      
      // Новый фильтр
      page.$el.on('click', '.create-filter', function(){
        app.request.get('./jira/filter/0', function(request){
          dialog_create_filter(request)
        })
      })
      
       // Новый фильтр
       page.$el.on('click', '.edit-filter', function(){
        let id = this.id
        app.request.get(`./jira/filter/${id}`, function(request){
          dialog_create_filter(request)
        })
      })

      page.$el.on('click', '.task_trace', function(){
        let id = this.id
        app.request.get(`./jira/worklog/trace/${id}`, function(request){
          let dynamicPopup = app.popup.create({
            content: request,
            // Events
            on: {
              open: function (popup) {
              },
              opened: function (popup) {
                console.log('Popup opened');
              },
            }
          });
          dynamicPopup.open()
        })
      })
      

    }
  }
})

var app = new Framework7({
    name: 'jiraworkflow', // App name
    theme: 'auto', // Automatic theme detectioz
    el: '#app', // App root element
    buttonOk: 'Ок',
    buttonCancel: 'Отменa',
    routes: routes,
    on: {
      pageInit: function () {
        console.log('APP INIT')
        popup_info($(document))
        // buttons 
      }
    }
  });

var mainView = app.views.create('#index', {
  url: '/index/'
});

function navigate(path, reload=true){
  app.view.current.router.navigate(path, {   
    ignoreCache: reload,
    reloadCurrent: reload,
    reloadAll: reload,
  })
}

const buttons = {
  'home': {
    text: 'Моя страница',
    cssClass: 'button button-raised button-fill button-round menu-button home darkslateblue',
    onClick: function(dialog, e){
      navigate('/profile/')
    }
  },
  'users': {
    text: 'Пользователи',
    cssClass: 'button button-raised button-fill button-round menu-button users',
    onClick: function(dialog, e){
      navigate('/users/')
    }
  },
  'repassword': {
    text: 'Профиль',
    cssClass: 'button button-raised button-fill button-round menu-button seagreen repassword',
    onClick: function(dialog, e){
      const settings = (content) => {
        return app.dialog.create({
        title: 'Настройки профиля',
        content: content,
        cssClass: 'dialog-profile',
        on: {
          opened: function (dialog) {
            console.log('dialog')
            let d = dialog.$el.find('.dialog-inner').append(
              $$('<span style="position: absolute;right: 20px;top: 20px;opacity: 0.3;" class="material-icons icon hover-op link dialog-close">highlight_off</span>')
            )
            // 
            console.log(d)
            dialog.$el.on('click', '.dialog-close', function(){
              app.dialog.close()
            })
            //
            dialog.$el.on('click', '.remove_current_user', function(){
              app.request.get('./accounts/remove', function(){
                app.toast.create({
                  icon: '<i class="material-icons">task_alt</i>',
                  text: 'Аккаунт удален',
                  position: 'center',
                  closeTimeout: 3000,
                }).open()
                navigate('/loginout/')
              })
            })
            //
            $('.form-ajax-submit').on('formajax:error', function(request) {
              console.log(JSON.parse(request.detail.xhr.response))
              app.notification.create({
                title: 'Изменение пароля',
                titleRightText: 'ошибка',
                subtitle: 'Исправте:',
                closeTimeout: 5000,
                closeButton: true,
                on: {
                  open: function(){
                    let content = this.$el.find('.notification-content')
                    let errors = $$('<div><ul style="font-size: 12px;"></ul></div>')
                    console.log(request)
                    for (msg of JSON.parse(request.detail.xhr.response).msg.new_password2){
                      errors.find('ul').append(
                        $$(`<li>${msg.message}</li>`)
                        )
                    }
                    content.append(errors)
                  }
                }
              }).open()
            })
            $('.form-ajax-submit').on('formajax:success', function(request) {
              app.notification.create({
                title: 'Изменение пароля',
                titleRightText: '',
                subtitle: 'Пароль изменен',
                closeTimeout: 3000,
              }).open()
            })
          }}
        })
      }
      app.request.get('./accounts/setting', function(request){
        let _dialog = settings(request)
            _dialog.open()
      })
    }
  },
  'jira': {
    text: 'Jira',
    cssClass: 'button button-raised button-fill button-round menu-button jira',
    onClick: function(dialog, e){
      navigate('/jira/')
    }
  },
  'timetta': {
    text: 'Timetta',
    cssClass: 'button button-raised button-fill button-round menu-button timetta',
    onClick: function(dialog, e){
      navigate('/timetta/')
    },
  },
  'out': {
    text: 'Выход',
    color: 'red',
    cssClass: 'button button-raised button-fill button-round menu-button out',
    onClick: function(dialog, e){
      navigate('/loginout/')
    }
  },
  'seporator': {
    text: '',
    color: '',
    cssClass: 'button button-seporator',
  }
}

const add_close_button = () => {
  return {
    opened: function () {
      this.$el.on('click', '.close-menu', function(){
        app.dialog.close()
      })
    },
    open: function (){
      console.log(this.$el.find('.dialog-inner'))
      this.$el.find('.dialog-inner').append(
        $$('<span style="position: absolute;right: 6px;top: 10px;opacity: 0.3;" class="material-icons icon hover-op link close-menu">highlight_off</span>')
      )
    }
  }
}

let menu_jira = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [buttons.home, buttons.users, buttons.timetta, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
  on: add_close_button()
})

let menu_home = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [ buttons.users, buttons.jira, buttons.timetta, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
  on: add_close_button()
})

let menu_timetta = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [buttons.home, buttons.users, buttons.jira, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
  on: add_close_button()
})

let menu_users = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [buttons.home, buttons.jira, buttons.timetta, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
  on: add_close_button()
})

$$(document).on('click', '.menu-home', function () {
  let superuser = $(this).attr('superuser')
  console.log(superuser)
  let dialog = menu_home.open();
  if (superuser == null){
    dialog.$el.find('span.users').css('display', 'none')
  }
  
});

$$(document).on('click', '.menu-jira', function () {
  let superuser = $(this).attr('superuser')
  let dialog = menu_jira.open();
  if (superuser == null){
    dialog.$el.find('span.users').css('display', 'none')
  }
});

$$(document).on('click', '.menu-users', function () {
  let superuser = $(this).attr('superuser')
  let dialog = menu_users.open();
  if (!superuser == null){
    dialog.$el.find('span.users').css('display', 'none')
  }
  
});

$$(document).on('click', '.menu-timetta', function () {
  let superuser = $(this).attr('superuser')
  let dialog = menu_timetta.open();
  if (!superuser == null){
    dialog.$el.find('span.users').css('display', 'none')
  }
  
});


