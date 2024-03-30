document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('acc_dr_visible').addEventListener("click", function(event) {
        event.preventDefault();
        document.getElementById('modal-account-list').style.display = "block";
        document.getElementById('modal-background').style.display = "block"
        document.getElementById('acc_type').value = 'dr';
        document.body.style.overflow = 'hidden';
    })

    document.getElementById('acc_cr_visible').addEventListener("click", function(event) {
        event.preventDefault();
        document.getElementById('modal-account-list').style.display = "block";
        document.getElementById('modal-background').style.display = 'block'
        document.getElementById('acc_type').value = 'cr';
        document.body.style.overflow = 'hidden';
    })

    document.getElementById('modal-background').addEventListener('click', function(event){
        document.getElementById('modal-background').style.display = 'none';
        document.getElementById('modal-account-list').style.display = 'none';
        document.body.style.overflow = 'auto';
    })

    let accItems = document.getElementsByClassName('acc-item')
    for(let i = 0; i < accItems.length; i++) {
        accItems[i].addEventListener("click", function(event) {
            let accPk = event.target.dataset.accpk
            if (document.getElementById('acc_type').value == 'dr') {
                document.getElementById('id_acc_dr').value = accPk;
                document.getElementById('acc_dr_visible').value = event.target.innerText;
            }
            else {
                document.getElementById('id_acc_cr').value = accPk;
                document.getElementById('acc_cr_visible').value = event.target.innerText;
            }
            document.getElementById('modal-account-list').style.display = "none";
            document.getElementById('modal-background').style.display = 'none';
            document.body.style.overflow = 'auto';
        })
    }

    let bookRows = document.getElementsByClassName('main-book-row')
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

    document.getElementById('show-entries').addEventListener('click', function(event) {
        window.location.href = location.protocol + '//' + location.host + location.pathname
            + '?date-from=' + document.getElementById('date-from').value + '&date-to=' + document.getElementById('date-to').value;
    });

})
