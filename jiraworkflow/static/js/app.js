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

// Профиль
routes.push({
  path: '/profile/',
  url: './profile'
})

// Разлогин
routes.push({
  path: '/loginout/',
  url: './accounts/login/out'
})

// Radis task list
routes.push({
  path: '/worklog/:task',
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
        //
        $$('.popup-sync-status').on('popup:closed', function (e, popup) {
          app.popup.destroy('.popup')
        })
        $$('.popup-sync-status').on('popup:open', function (e) {

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

          /*
          var json_codemirror = CodeMirror.fromTextArea(
              $(e.target).find('#json')[0],
              {
                "matchBrackets": true,
                "mode": "application/json",
                "continueComments": "Enter",
                "fullScreen": true,
                "extraKeys": {"Ctrl-Q": "toggleComment"}, 
                "lineNumber": false, 
                "indent": 4,
                "readOnly": true
              }
          );
          console.log(json_codemirror)
          */
        });
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
        //
        app.toast.create({
          icon: '<i class="material-icons">task_alt</i>',
          text: 'Сохранено',
          position: 'center',
          closeTimeout: 2000,
        }).open() 
        //
      })
      
      var dialog_create = (content) => {
        var dialog = app.dialog.create({
        title: 'Проект',
        content: content,
        cssClass: 'dialog-project',
        on: {
          opened: function (dialog) {

            jQuery('#project_list').mCustomScrollbar({advanced:{ updateOnSelectorChange: "li", autoScrollOnFocus: "ul li", }})
            jQuery('#task_list').mCustomScrollbar({advanced:{ updateOnSelectorChange: "li", autoScrollOnFocus: "ul li" }})

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

            dialog.$el.on('click', '.get-task-list', function(){
              let project = $$(this).attr('project')
              let $task_el = dialog.$el.find("#id_task_id")
                  $task_el.val('')
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

            dialog.$el.on('change', 'input[name="project-task"]', function(){
            let $el = dialog.$el.find("#id_task_id")
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
      navigate('/repassword/')
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

let menu_jira = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [buttons.home, buttons.users, buttons.timetta, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
})

let menu_home = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [ buttons.users, buttons.jira, buttons.timetta, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
})

let menu_timetta = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [buttons.home, buttons.users, buttons.jira, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
})

let menu_users = app.dialog.create({
  title: 'Меню',
  cssClass: 'dialog-nemu',
  buttons: [buttons.home, buttons.jira, buttons.timetta, buttons.seporator, buttons.repassword, buttons.out],
  verticalButtons: true,
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
