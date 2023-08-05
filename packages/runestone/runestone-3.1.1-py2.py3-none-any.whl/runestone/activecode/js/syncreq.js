const fetch = require("node-fetch");


const requestAnimePromise = id => {
    fetch(`https://jikan.me/api/anime/${id}`)
        .then(response => response.json())
        .then(json => {
            console.log("Promise-based")
            console.log(json)
        });
}

requestAnimePromise(1);


const requestAnimeAwait = async (id=100) => {
    const response = await fetch(`https://jikan.me/api/anime/${id}`)
    const json = await response.json();
    console.log("async/await based");
    console.log(json);
}

requestAnimeAwait();
