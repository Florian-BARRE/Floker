function info_update(id, infos, template, skip_first_row = true) {
    update_nb_rows(id, infos.length + skip_first_row, template.length);
    set_row(id, Number(skip_first_row), infos);
}

function perf_update(){
    info_update(id, infos, PERFORMANCE_INFOS_TEMPLATE);
    
}