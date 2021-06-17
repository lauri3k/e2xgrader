let Task = Backbone.Model.extend({
    idAttribute: 'name',
    urlRoot: base_url + '/taskcreator/api/task/' + pool
});

let Tasks = Backbone.Collection.extend({
    model: Task,
    url: base_url + '/taskcreator/api/pools/' + pool
});

let TaskUI = BaseUI.extend({

    events: {},

    initialize: function () {
        this.$task_name = this.$el.find('.task-name');
        this.$number_of_questions = this.$el.find('.number-of-questions');
        this.$points = this.$el.find('.points');
        this.$edit_task = this.$el.find('.edit-task');
        this.$remove_task = this.$el.find('.remove-task');

        this.fields = [this.$task_name, this.$number_of_questions, 
                       this.$points, this.$edit_task, this.$remove_task];

        this.listenTo(this.model, 'sync', this.render);
        this.render();
    },

    render: function () {
        this.clear();
        let name = this.model.get('name');
        //this.$task_name.text(name);
        this.$task_name.append($('<a/>')
            .attr('href', tree_url + 'pools/' + pool + '/' + name)
            .text(name));
        this.$points.text(this.model.get('points'));
        this.$number_of_questions.text(this.model.get('questions'));
        this.$edit_task.append($('<a/>')
            .attr('href', notebook_url + 'pools/' + pool + '/' + name + '/' + name + '.ipynb')
            .text('Edit'));
        this.$remove_task.append($('<a/>')
            .attr('href', '#')
            .click(_.bind(this.removeTaskModal, this))
            .append($('<span/>').text('Remove')
                ));
    },

    removeTaskModal: function() {
        let body = $('<div/>');
        body.append($('<p/>').text('Are you sure you want to delete the task?'));
        body.append($('<p/>').text('This action can\'t be undone!'));

        this.openRemoveModal(body, "Delete task " + this.model.get('name') + "?");
    },

});

function insertRow(table) {
    let row = $('<tr/>');
    row.append($('<td/>').addClass('task-name'));
    row.append($('<td/>').addClass('number-of-questions'));
    row.append($('<td/>').addClass('points'));
    row.append($('<td/>').addClass('edit-task'));
    row.append($('<td/>').addClass('remove-task'));
    table.append(row);
    dataTable.row.add(row).draw();
    return row;
}

function addView(model, table) {
    let view = new TaskUI({
        'model': model,
        'el': insertRow(table)
    });
    views.push(view);
    return view;
}

function loadTasks() {
    let tbl = $('#main_table');
    models = new Tasks();
    views = [];
    models.loaded = false;
    models.fetch({
        success: function () {
            tbl.empty();
            dataTable = tbl.parent().DataTable({
                'columnDefs': [
                    {'orderable': false, 'targets': [-1, -2]},
                    {'searchable': false, 'targets': [-1, -2]}
                ]
            });
            models.each((model) => addView(model, tbl));
            
            models.loaded = true;
        }
    })

}

function newTask() {
    let body = $('<div/>').append($('</p>').text(
        `Please specify the name of the new task. Names can consist of characters, 
         digits, spaces and underscores.`));
    let table = $('<table/>').addClass('table table-striped form-table');
    let tablebody = $('<tbody/>');
    body.append(table);
    table.append(tablebody);
    let name = $('<tr/>');
    tablebody.append(name);
    name.append($('<td/>').addClass('align-middle').text('Name'));
    name.append($('<td/>').append($('<input/>')
        .addClass('modal-name')
        .attr('pattern', '[A-Za-z0-9]+')
        .attr('type', 'text')));
    let footer = $('<div/>');
    footer.append($('<button/>')
        .addClass('btn btn-primary save')
        .text('Add Task'));
    footer.append($('<button/>')
        .addClass('btn btn-danger')
        .attr('data-dismiss', 'modal')
        .text('Cancel'));

    $modal = createModal("new-task-modal", "Create a new task", body, footer);
    
    $modal_save = $modal.find('button.save');
    $modal_save.click(function () {
        $modal_name = $modal.find('input.modal-name').val();
        let task = new Task();
        task.save({
            'name': $modal_name,
            'tasks': 0
        }, {
            success: function(task) {
            if (task.get('success')) {
                $modal.modal('hide');
                let view = addView(task, $('#main_table'));
                models.add([task]);
            } else {
                createLogModal(
                    'error-modal',
                    'Error',
                    'There was an error creating the task ' + task.get('name') + '!',                    
                    task.get('error'));
            }
        }});
    })

}

let models = undefined;
let views = [];
let dataTable = undefined;

$(window).on('load', function () {
    loadTasks();
})
