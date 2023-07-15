async function send_request(url) {
    let data;
    await fetch(url)
        .then(response => response.json())
        .then(jsonData => {
            data = jsonData;
            console.log(data);
        })
        .catch(error => console.error(error))
    return data;
}


async function get_topics(only_extraction = false) {
    let data = await send_request(TOPICS_VIEWER_URL);
    if (only_extraction === true)
        return data["extraction"];
    else
        return data;
}


async function get_history(only_extraction = false) {
    let data = await send_request(HISTORY_VIEWER_URL);
    if (only_extraction === true)
        return data["extraction"];
    else
        return data;
}