define([
    'require',
    'jquery',
    'base/js/namespace',
    'base/js/events',
], function (
    requirejs,
    $,
    Jupiter
) {
    "use strict";

    var is_solution = function(cell) {
        if (cell.metadata.nbgrader === undefined) {
            return false;
        } else if (cell.metadata.nbgrader.solution === undefined) {
            return false;
        } else {
            return cell.metadata.nbgrader.solution;
        }
    };

    var is_grade = function(cell) {
        if (cell.metadata.nbgrader === undefined) {
            return false;
        } else if (cell.metadata.nbgrader.grade === undefined) {
            return false;
        } else {
            return cell.metadata.nbgrader.grade;
        }
    };

    var gradeLabel = '<div class="grade-label" style="padding: 8px 0;">' +
                     '<span class="label label-warning">С оценкой</span>' +
                     '</div>';

    function add_labels() {
        var cells = Jupyter.notebook.get_cells();

        cells.forEach(function(cell) {
            if (!is_grade(cell) && !is_solution(cell)) {
                return;
            }

            var inner_cell = cell.element.find('.inner_cell');
            $(inner_cell).prepend(gradeLabel);
        });
    }


    function load_extension() {
        add_labels();
        console.log('nbgrader extension for display grade label loaded')
    }

    return {
        load_ipython_extension: load_extension,
    }
});