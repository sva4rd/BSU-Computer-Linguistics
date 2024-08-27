#include "editwindow.h"

EditWindow::EditWindow(QWidget* pwgt):QDialog(pwgt)
{
    setWindowTitle("Edit Item");
    input = new QLineEdit(this);
    editTexts = new QCheckBox(this);
    editTexts->setText("Change the word in the texts");
    okButton = new QPushButton(this);
    okButton->setText("Ok");
    cancelButton = new QPushButton(this);
    cancelButton->setText("Cancel");

    buttonLay = new QHBoxLayout;
    buttonLay->addStretch(1);
    buttonLay->addWidget(okButton);
    buttonLay->addWidget(cancelButton);

    mainLay = new QVBoxLayout(this);
    mainLay->addWidget(input);
    mainLay->addWidget(editTexts);
    mainLay->addLayout(buttonLay);

    setMaximumSize(300, 140);
    connect(okButton, &QPushButton::clicked, this, &EditWindow::checkData);
    connect(cancelButton, SIGNAL(clicked()), SLOT(reject()));
}

void EditWindow::setValidator(QValidator* val)
{
    input->setValidator(val);
}

void EditWindow::setText(QString modifiedWord)
{
    input->setText(modifiedWord);
}

void EditWindow::checkData()
{
    if (!input->text().isEmpty() && input->text().last(1) != '-'){
        emit(modifiedData(input->text(), editTexts->isChecked()));
        accept();
        return;
    }
    QMessageBox::warning(this, "Error", "Misspelling");
    return;
}
