async function getReviews(){
    return fetch("{% url 'main:show_json' %}").then((res) => res.json())
}
