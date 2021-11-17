import '@testing-library/jest-dom'
// const JSDOM = require('jsdom')
import { JSDOM } from 'jsdom'
import fs from 'fs'
import path from 'path'

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

let dom
let container

describe('index.html', () => {
    beforeEach(() => {
        // Constructing a new JSDOM with this option is the key
        // to getting the code in the script tag to execute.
        // This is indeed dangerous and should only be done with trusted content.
        // https://github.com/jsdom/jsdom#executing-scripts
        dom = new JSDOM(html, { runScripts: 'dangerously' })
        container = dom.window.document.body
    })


    it('check for start record button', () => {
        expect(container.querySelector('#button-start')).not.toBeNull()
    })

    it('check for stop record button', () => {
        expect(container.querySelector('#button-stop')).not.toBeNull()
    })

    it('check for message textareas', () => {
        expect(container.querySelector('#message_user')).not.toBeNull()
        expect(container.querySelector('#message_watson')).not.toBeNull()
    })

})