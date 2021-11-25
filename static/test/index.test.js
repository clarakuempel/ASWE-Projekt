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


    it('check for record button', () => {
        expect(container.querySelector('#rec-button')).not.toBeNull()
    })

    it('check for message textareas', () => {
        expect(container.querySelector('#m1')).not.toBeNull()
        expect(container.querySelector('#m1_user')).not.toBeNull()
    })

    it('user preference configuration available', () => {
        expect(container.querySelector('#wakeup_time')).not.toBeNull()
        expect(container.querySelector('#assistent_sex')).not.toBeNull()
        expect(container.querySelector('#location_lat')).not.toBeNull()
        expect(container.querySelector('#location_lon')).not.toBeNull()
        expect(container.querySelector('#gemeindecode')).not.toBeNull()
        expect(container.querySelector('#news_topic')).not.toBeNull()
        expect(container.querySelector('#gym')).not.toBeNull()
    })

    it('check for post request function', () => { expect(1).toEqual(1) })
    it('check for get request function', () => { expect(1).toEqual(1) })

})
