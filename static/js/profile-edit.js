function editField(fieldName) {
    document.getElementById(fieldName + '-display-container').style.display = 'none';
    document.getElementById(fieldName + '-form').style.display = 'block';
}

function cancelEdit(fieldName) {
    document.getElementById(fieldName + '-display-container').style.display = 'flex';
    document.getElementById(fieldName + '-form').style.display = 'none';
}
