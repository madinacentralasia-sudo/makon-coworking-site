// Makon — saytdan kelgan arizalar.
// Har bir ariza "Makon — saytdan arizalar" jadvaliga yoziladi va Telegram guruhiga xabar bo'lib keladi.
// Bu kod Google Apps Script'da, jadvalga ulangan holda turadi (Kengaytmalar → Apps Script).
//
// Sozlamalar (Project Settings → Script properties):
//   TG_TOKEN     — Telegram bot kaliti (maxfiy, faqat egasi kiritadi)
//   TG_CHAT_ID   — arizalar keladigan Telegram chat ID (hozir Kamolaning shaxsiy chati)
//   TG_THREAD_ID — (ixtiyoriy) guruh mavzusi ID raqami, guruhga yuborilsa

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p._honey) return javob_('ok'); // spam-bot to'ldirgan yashirin maydon

  var ism = (p.ism || '').trim();
  var tel = (p.telefon || '').trim();
  if (!ism || !tel) return javob_('empty');
  var faol = (p.faoliyat || '').trim();
  var qiz = (p.qiziqish || '').trim();
  var til = (p.til || '').trim().toLowerCase();
  var vaqt = Utilities.formatDate(new Date(), 'Asia/Tashkent', 'dd.MM.yyyy, HH:mm');

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    SpreadsheetApp.getActiveSpreadsheet()
      .getSheetByName('Arizalar')
      .appendRow([vaqt, ism, "'" + tel, faol, qiz]);
  } finally {
    lock.releaseLock();
  }

  try {
    telegram_(vaqt, ism, tel, faol, qiz, til);
  } catch (err) {
    console.error(err);
  }
  return javob_('ok');
}

function telegram_(vaqt, ism, tel, faol, qiz, til) {
  var pr = PropertiesService.getScriptProperties();
  var token = pr.getProperty('TG_TOKEN');
  var chat = pr.getProperty('TG_CHAT_ID');
  if (!token || !chat) return;

  var matn =
    '🆕 Makon: yangi ariza\n' +
    'Ism: ' + ism + '\n' +
    'Telefon: ' + tel + '\n' +
    'Faoliyat: ' + (faol || '—') + '\n' +
    'Qiziqish: ' + (qiz || '—') + '\n' +
    (til && til !== 'uz' ? 'Til: ' + til.toUpperCase() + '\n' : '') +
    'Sana: ' + vaqt;

  var data = { chat_id: chat, text: matn };
  var thread = pr.getProperty('TG_THREAD_ID');
  if (thread) data.message_thread_id = Number(thread);

  UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(data),
    muteHttpExceptions: true
  });
}

function javob_(t) {
  return ContentService.createTextOutput(t);
}

// Bot ochilib, unga /start yozilgandan keyin bir marta ishga tushiriladi.
// Jurnalga (Execution log) chat ID'sini chiqaradi — uni TG_CHAT_ID ga yoziladi.
function guruhniTopish() {
  var token = PropertiesService.getScriptProperties().getProperty('TG_TOKEN');
  var r = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/getUpdates', { muteHttpExceptions: true });
  var upd = JSON.parse(r.getContentText()).result || [];
  var jj = JSON.parse(r.getContentText());
  Logger.log('Kod: ' + r.getResponseCode() + ' | ok: ' + jj.ok + ' | ' + (jj.description || '') + ' | kalit uzunligi: ' + (token ? token.length : 0));
  var me = JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/getMe', { muteHttpExceptions: true }).getContentText());
  Logger.log('Bot: @' + (me.result ? me.result.username : '?'));
  Logger.log('Topildi: ' + upd.length);
  upd.forEach(function (u) {
    var m = u.message || u.my_chat_member;
    if (!m || !m.chat) return;
    Logger.log(m.chat.id + ' | ' + (m.chat.title || '') + ' | mavzu: ' + (m.message_thread_id || '-') + ' | ' + (m.text || ''));
  });
}

// Telegram ulanishini tekshirish: sinov xabar yuboradi va javobni jurnalga yozadi.
function telegramSinov() {
  var pr = PropertiesService.getScriptProperties();
  var token = pr.getProperty('TG_TOKEN');
  var chat = pr.getProperty('TG_CHAT_ID');
  var r = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ chat_id: chat, text: 'Makon arizalar: sinov xabari' }),
    muteHttpExceptions: true
  });
  var j = JSON.parse(r.getContentText());
  Logger.log('Kod: ' + r.getResponseCode() + ' | ok: ' + j.ok + ' | ' + (j.description || '') + ' | chat: ' + chat);
}
