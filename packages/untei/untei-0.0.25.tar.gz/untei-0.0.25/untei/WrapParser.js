let parser = require('./MarkdownParser')
let fs     = require('fs')

let markdown_path     = process.argv[2]
let parse_result_json = parser.parse(fs.readFileSync(markdown_path, 'utf-8'))
console.log(JSON.stringify(parse_result_json))