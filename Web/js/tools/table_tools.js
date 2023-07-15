function get_table(id) {
    return document.getElementById(id);
}

function get_cell(id, i, j) {
    return get_table(id).rows[i].cells[j];
}

function get_value(id, i, j) {
    return get_cell(id, i, j).innerHTML;
}

function set_value(id, i, j, val) {
    get_cell(id, i, j).innerHTML = val;
}

function set_row(id, l, values){
    for(let c=0; c<values.length; c++)
        set_value(id, l, c, values[c]);
}

function update_nb_rows(id, target_rows, target_cols=null){
    let table = get_table(id);
    let nb_rows = table.rows.length;
    let nb_cols = 0;
    if (nb_rows > 0)
        nb_cols = table.rows[0].cells.length;

    if (nb_cols !== target_cols){
        table.innerHTML = generate_html_table(target_rows, target_cols);
    }
    else if(nb_rows < target_rows){
        table.innerHTML += generate_html_table(target_rows - nb_rows, target_cols);
    }
    else if (nb_rows > target_rows) {
        table.innerHTML = generate_html_table(target_rows, target_cols);
    }
}

function create_table(id, table_rows = 1, table_cols = 1) {
    get_table(id).innerHTML = generate_html_table(table_rows, table_cols);
}