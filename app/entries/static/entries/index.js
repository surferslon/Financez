class EntriesListComponent extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.fetchData();
        document.getElementById("new-entry-form").addEventListener("submit", this.createEntry.bind(this))
        document.getElementById("date-from").addEventListener("change", this.fetchData.bind(this))
        document.getElementById("date-to").addEventListener("change", this.fetchData.bind(this))
    }
    fetchData() {
        const periodFrom = document.getElementById("date-from").value;
        const periodTo = document.getElementById("date-to").value;
        this.innerHTML = "";
        fetch(`${this.getAttribute("data-url-list")}?date-from=${periodFrom}&date-to=${periodTo}`)
            .then(response => response.json())
            .then(data => this.renderData(data));
    }
    addRow(entry) {
        const entryEl = document.createElement("div");
        entryEl.className = "main-book-row";
        entryEl.dataset.updateUrl = entry.update_url;
        entryEl.dataset.readUrl = entry.read_url;
        entryEl.onclick = this.showEditEntry;
        entryEl.innerHTML = `
            <div class="main-book-item">${entry.date}</div>
            <div class="main-book-item">${entry.acc_dr__name }</div>
            <div class="main-book-item">${entry.acc_cr__name }</div>
            <div class="main-book-item" style="text-align: right;">${ entry.total } </div>
            <div class="main-book-item" style="padding-left: 10px">${ entry.comment }</div>
        `;
        this.prepend(entryEl);
    }
    renderData(data) {
        data.forEach(entry => {this.addRow(entry);});
    }
    createEntry(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const url = event.target.getAttribute("action");
        const csrfToken = event.target.querySelector('input[name="csrfmiddlewaretoken"]').value;
        fetch(url, {method: "POST", body: formData, headers: {"X-CSRFToken": csrfToken}})
            .then(resp => {
                document.getElementById("id_total").value = "";
                document.getElementById("id_comment").value = "";
                this.fetchData();
            })
    }
    showEditEntry() {
        fetch(this.dataset.readUrl)
            .then(response => response.text())
            .then(template => {
                const modal = new EditEntryModal();
                modal.innerHTML = template;
                modal.updateUrl = this.dataset.updateUrl;
                modal.entryRow = this;
                document.body.appendChild(modal);
            })
    }
}

class SelectAccountModal extends HTMLElement {
    constructor() {
        super();
        this.inputField = null;
        this.inputValue = null;
        this.closeBg = null;
    }
    connectedCallback() {
        this.fetchTemplate();
    }
    fetchTemplate() {
        const url = document.getElementById("new-entry-form").getAttribute("data-modal-url");
        fetch(url)
            .then(response => response.text())
            .then(template => this.render(template));
    }
    render(template) {
        document.getElementById("modal-background").style.display = "block";
        document.body.style.overflow = "hidden";
        this.innerHTML = template
        this.assignEvents();
    }
    assignEvents() {
        let accItems = this.getElementsByClassName("acc-item")
        for(let i = 0; i < accItems.length; i++) {
            accItems[i].addEventListener("click", (event) => {
                this.inputField.value = event.target.innerText;;
                this.inputValue.value = event.target.dataset.accpk
                this.close();
            })
        }
    }
    close () {
        document.body.style.overflow = 'auto';
        if (this.closeBg) {
            document.getElementById("modal-background").style.display = "none";
        }
        this.remove();
    }
}

class EditEntryModal extends HTMLElement {
    constructor() {
        super();
        this.udpateUrl = null;
        this.entryRow = null;
    }
    connectedCallback() {
        document.getElementById("modal-background").style.display = "block";
        document.body.style.overflow = "hidden";
        this.assignEvents();
    }
    assignEvents() {
        this.querySelector("#acc_dr_input").addEventListener(
            "click", function(event) {showSelectAccount(event, false)}
        )
        this.querySelector("#acc_cr_input").addEventListener(
            "click", function(event) {showSelectAccount(event, false)}
        )
        this.querySelector("#saveEntryBtn").addEventListener("click", this.saveEntry.bind(this))
    }
    saveEntry(event) {
        event.preventDefault();
        const formData = new FormData(this.querySelector("#edit-entry-form"));
        const csrfToken = this.querySelector('input[name="csrfmiddlewaretoken"]').value;
        fetch(this.updateUrl, {method: "PATCH", body: formData, headers: {"X-CSRFToken": csrfToken}})
        .then(response => response.json())
        .then(data => {
            this.entryRow.innerHTML = `
                <div class="main-book-item">${data.date}</div>
                <div class="main-book-item">${data.acc_dr__name }</div>
                <div class="main-book-item">${data.acc_cr__name }</div>
                <div class="main-book-item" style="text-align: right;">${ data.total } </div>
                <div class="main-book-item" style="padding-left: 10px">${ data.comment }</div>
            `;
        })
        this.close();
    }
    close() {
        document.body.style.overflow = 'auto';
        document.getElementById("modal-background").style.display = "none";
        this.remove()
    }
}


function showSelectAccount(event, closeBg=true) {
    event.preventDefault();
    const modal = document.createElement("select-account-modal")
    modal.inputField = event.target;
    modal.inputValue = event.target.nextElementSibling;
    modal.closeBg = closeBg;
    document.body.appendChild(modal)
}


document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("acc_dr_input").addEventListener(
        "click", function(event) {showSelectAccount(event)}
    )
    document.getElementById("acc_cr_input").addEventListener(
        "click", function(event) {showSelectAccount(event)}
    )
    document.getElementById('modal-background').addEventListener('click', function(event){
        document.getElementById('modal-background').style.display = 'none';
        document.body.style.overflow = 'auto';
        const acc_modal = document.querySelector('select-account-modal');
        if (acc_modal) {
            acc_modal.remove();
        }
        const edit_modal = document.querySelector('edit-entry-modal');
        if (edit_modal) {
            edit_modal.remove();
        }
    })

    let bookRows = document.getElementsByClassName("main-book-row")
    for(let i = 0; i < bookRows.length; i++) {
        bookRows[i].addEventListener("mouseenter", function(event) {
            const els = document.getElementsByClassName(event.target.classList[1])
            Array.from(els).forEach(function(element) {
                element.style.backgroundColor = '#fafafa';
            });
        })
        bookRows[i].addEventListener("mouseleave", function(event) {
            const els = document.getElementsByClassName(event.target.classList[1])
            Array.from(els).forEach(function(element) {
                element.style.backgroundColor = 'white';
            });
        })
    }
})

customElements.define("entries-list-component", EntriesListComponent);
customElements.define("select-account-modal", SelectAccountModal);
customElements.define("edit-entry-modal", EditEntryModal);
