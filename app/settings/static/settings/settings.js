function changeCurrency(event){
    let cur_id = event.target.dataset.curid;
    let {url} = document.querySelector('.currencies-list').dataset;
    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams({
            cur_pk: cur_id
        })
    })
    .then(resp => {
        if (resp.status === 200) {
            window.location.reload(true);
        }
        else {
            console.error('Error:', resp.status);
        }
    });
}


function changeSection(section){
    document.querySelectorAll('.set-menu-item').forEach(item => {
        if (item.id === `menu-${section}`) {
            item.classList.add('set-menu-item-active');
        }
        else {
            item.classList.remove('set-menu-item-active');
        }
    })
    if (section === 'general') {
        document.querySelector('#general-settings').style.display = 'block';
        document.querySelector('#account-settings').style.display = 'none';
    }
    else {
        document.querySelector('#general-settings').style.display = 'none';
        document.querySelector('#account-settings').style.display = 'block';
    }
}


function assignListeners() {
    document.querySelectorAll('.set-menu-item').forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();
            const section = item.id.replace('menu-', '');
            changeSection(section);
        });
    });

    document.querySelectorAll('.acc-tree-item').forEach(function(item) {
        item.addEventListener('change', function(event) {
            let elem = event.target;
            let acc_pk = elem.parentElement.dataset.accpk;
            let acc_field = elem.dataset.field;
            fetch(document.querySelector('#acc-list').dataset.url, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    acc_pk: acc_pk,
                    acc_field: acc_field,
                    value: elem.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (['parent', 'results'].includes(acc_field)) {
                    window.location.reload(true);
                }
            });
        });
    });

    document.querySelectorAll('.cur-button').forEach(function(button) {
        button.addEventListener('click', event => changeCurrency(event));
    });

    document.querySelector('#language-selector').addEventListener('change', function(event) {
        document.querySelector('#language-form').submit();
    });

    document.querySelector('#new-acc-button').addEventListener('click', function(event) {
        document.querySelector('#modal-background').style.display = 'flex';
        document.querySelector('#modal-new-acc').style.display = 'block';
        document.body.style.overflow = 'hidden';
    });

    document.querySelector('#add-currency-button').addEventListener('click', function(event) {
        event.preventDefault();
        document.querySelector('#modal-background').style.display = 'flex';
        document.querySelector('#modal-new-cur').style.display = 'block';
        document.body.style.overflow = 'hidden';
    });

    document.querySelectorAll('.del-button').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            document.querySelector('#modal-background').style.display = 'flex';
            document.querySelector('#modal-del-acc').style.display = 'block';
            document.querySelector('#form-del-acc').action = event.target.href;
        });
    });

    document.querySelector('#modal-background').addEventListener('click', function(event) {
        document.querySelector('#modal-background').style.display = 'none';
        document.querySelector('#modal-new-acc').style.display = 'none';
        document.querySelector('#modal-new-cur').style.display = 'none';
        document.querySelector('#modal-del-acc').style.display = 'none';
        document.body.style.overflow = 'auto';
    });
}


document.addEventListener('DOMContentLoaded', function() {
    changeSection('general');
    assignListeners();
});
