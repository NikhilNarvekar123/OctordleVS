const express = require('express')
const axios = require('axios')
const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.get('/word', (req, res) => {
    const url = 'https://random-word-api.vercel.app/api?words=1&length=5';
    axios.get(url)
    .then((response) => {
        console.log(response.data)
        res.json(response.data)
    }).catch((error) => {
        console.error(error)
    })
})


app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})