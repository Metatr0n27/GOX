function createGoxFamilyIntake() {
  const form = FormApp.create('GOX Family Profile Intake');
  form.setDescription(
    'Phone-friendly intake for GOX family profiles. Complete this only for yourself. ' +
    'Your answers help GOX adapt how it communicates, teaches, plans, and assists you.'
  );
  form.setConfirmationMessage('Done. Your GOX family profile response was saved.');
  form.setProgressBar(true);
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);

  form.addSectionHeaderItem().setTitle('Identity and consent');
  form.addTextItem().setTitle('Your name').setRequired(true);
  form.addTextItem().setTitle('How should GOX address you?').setRequired(true);
  form.addTextItem().setTitle('Relationship / family label (optional)');
  form.addMultipleChoiceItem()
    .setTitle('Do you agree to have these answers used to create your personal GOX profile?')
    .setChoiceValues(['Yes', 'No'])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('May this profile be stored in the shared family GOX system?')
    .setChoiceValues(['Yes', 'No'])
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('How you naturally operate');
  addScale(form, 'How quickly do you usually make decisions?', 'Very slowly / need time', 'Very quickly / decide fast');
  addScale(form, 'How comfortable are you with risk?', 'Avoid risk', 'Comfortable with risk');
  addScale(form, 'How much structure do you prefer?', 'Loose / flexible', 'Very structured');
  addScale(form, 'How direct are you when communicating?', 'Very indirect', 'Very direct');
  addScale(form, 'How social are you when solving problems?', 'Prefer working alone', 'Prefer involving people');
  addScale(form, 'How comfortable are you with sudden changes?', 'Strongly dislike change', 'Adapt quickly');

  form.addMultipleChoiceItem()
    .setTitle('When there is conflict, what do you most often do?')
    .setChoiceValues(['Avoid it', 'Discuss it calmly', 'Address it directly', 'Try to mediate', 'Compete / push my position', 'It depends'])
    .setRequired(true);

  form.addParagraphTextItem().setTitle('What do you tend to do when you are stressed or overwhelmed?').setRequired(true);
  form.addParagraphTextItem().setTitle('What makes you trust a person or system?').setRequired(true);
  form.addParagraphTextItem().setTitle('How do you learn best? Give examples if useful.').setRequired(true);
  form.addParagraphTextItem().setTitle('How do you prefer people or AI to communicate with you?');
  form.addParagraphTextItem().setTitle('What motivates you the most?');
  form.addParagraphTextItem().setTitle('What tends to frustrate or shut you down?');

  form.addSectionHeaderItem().setTitle('What you want GOX to do for you');
  form.addParagraphTextItem().setTitle('What is the biggest thing you want help with right now?').setRequired(true);
  form.addParagraphTextItem().setTitle('What should GOX do automatically for you?').setRequired(true);
  form.addParagraphTextItem().setTitle('What should GOX NOT do for you?');
  form.addParagraphTextItem().setTitle('What skills would you like to build?');
  form.addParagraphTextItem().setTitle('Do you have any project, work, business, or income goals?');

  form.addSectionHeaderItem().setTitle('Real behavior examples');
  form.addParagraphTextItem().setTitle('When things are going well, what are you usually like?').setRequired(true);
  form.addParagraphTextItem().setTitle('When you get frustrated, what are you usually like?').setRequired(true);
  form.addParagraphTextItem().setTitle('How do you normally make an important decision?').setRequired(true);
  form.addParagraphTextItem().setTitle('How do you usually ask for help?');
  form.addParagraphTextItem().setTitle('What makes you feel respected when someone is helping you?');
  form.addParagraphTextItem().setTitle('Tell one real story that shows how you react, solve problems, or make decisions.');

  const sheet = SpreadsheetApp.create('GOX Family Profiles - Responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  const instructions = sheet.insertSheet('GOX Instructions');
  instructions.getRange('A1:B8').setValues([
    ['GOX Family Intake', 'Phone-first setup for up to 10+ family members'],
    ['Public form URL', form.getPublishedUrl()],
    ['Edit form URL', form.getEditUrl()],
    ['Responses sheet URL', sheet.getUrl()],
    ['How to use', 'Text the Public form URL to each family member. Each person completes it from their own phone browser.'],
    ['Accounts required', 'Respondents do not need a Google account unless you later change the Form settings to require sign-in.'],
    ['Privacy', 'Do not ask for passwords, financial credentials, medical records, or other secrets in this form.'],
    ['GOX import', 'Export the responses tab as CSV when you are ready to import profiles into GOX.']
  ]);
  instructions.autoResizeColumns(1, 2);

  Logger.log('FORM: ' + form.getPublishedUrl());
  Logger.log('EDIT: ' + form.getEditUrl());
  Logger.log('SHEET: ' + sheet.getUrl());
}

function addScale(form, title, lowLabel, highLabel) {
  form.addScaleItem()
    .setTitle(title)
    .setBounds(1, 5)
    .setLabels(lowLabel, highLabel)
    .setRequired(true);
}
