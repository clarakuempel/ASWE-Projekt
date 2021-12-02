import '@testing-library/jest-dom/extend-expect'
import { JSDOM } from 'jsdom'
import fs from 'fs'
import path from 'path'

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

let dom
let container

describe('index.html', () => {
    beforeEach(() => {
        dom = new JSDOM(html, { runScripts: 'dangerously' })
        container = dom.window.document.body
    })

    it('check for record button', () => {
        expect(container.querySelector('#rec-button')).not.toBeNull()
    })

    it('check for response messages', () => {
        expect(container.querySelector('#m1')).not.toBeNull()
        expect(container.querySelector('#m2')).not.toBeNull()
    })

    it('check for user messages', () => {
        expect(container.querySelector('#m1_user')).not.toBeNull()
    })

    it('check for link and thumbnail', () => {
        expect(container.querySelector('#m2_extra1')).not.toBeNull()
        expect(container.querySelector('#m2_extra2')).not.toBeNull()
    })

    it('user preference configuration available', () => {
        expect(container.querySelector('#username')).not.toBeNull()
        expect(container.querySelector('#assistent_sex')).not.toBeNull()
        expect(container.querySelector('#location_lat')).not.toBeNull()
        expect(container.querySelector('#location_lon')).not.toBeNull()
        expect(container.querySelector('#gemeindecode')).not.toBeNull()
        expect(container.querySelector('#news_topic')).not.toBeNull()
        expect(container.querySelector('#gym')).not.toBeNull()
        expect(container.querySelector('#wakeup_time')).not.toBeNull()
    })

    it('check save pref', () => {
        expect(container.querySelector('#savePref')).not.toBeNull()
    })

    it('check for demo trigger buttons UC2-4', () => {
        expect(container.querySelector('#UC2')).not.toBeNull()
        expect(container.querySelector('#UC3')).not.toBeNull()
        expect(container.querySelector('#UC4')).not.toBeNull()
    })
})
