function generate_html_table(nb_row, nb_col) {
    let open_row = "<tr>";
    let close_row = "</tr>";

    let open_col = "<td>";
    let close_col = "</td>";

    let html = "";

    for (let l = 0; l < nb_row; l++) {
        html += open_row;
        for (let c = 0; c < nb_col; c++) {
            html += open_col + close_col;
        }
        html += close_row;
    }

    return html;
}
