function general_info_update(infos, skip_first_row = true){
    update_nb_rows(GENERAL_INFO_TABLE_ID, infos.length + skip_first_row, GENERAL_INFOS_TEMPLATE.length);
    set_row(GENERAL_INFO_TABLE_ID, Number(skip_first_row), infos);

}