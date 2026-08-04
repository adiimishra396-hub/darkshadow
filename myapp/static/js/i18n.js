/*
 * Darkshadow language switcher — English (default), Hindi, Hinglish.
 * Client-side only: translates elements marked with data-i18n / data-i18n-html
 * (and data-i18n-ph for placeholders) and persists the choice in
 * localStorage so it carries across page navigations.
 *
 * {amt} inside a translation string is replaced with the site's signup
 * bonus amount, read from <body data-bonus="...">, so translated strings
 * stay correct if the admin changes the bonus.
 */
(function () {
  var DS_I18N = {
    en: {
      nav_games: 'Games',
      nav_all_games: 'All Games',
      nav_promotions: 'Promotions',
      nav_how: 'How It Works',
      nav_contact: 'Contact',
      nav_home: 'Home',
      btn_login: 'Log In',
      btn_joinnow: 'Join Now',
      btn_logout: 'Log Out',
      dd_addmoney: 'Add Money',
      dd_mywallet: 'My Wallet',
      dd_editprofile: 'Edit Profile',
      dd_changepassword: 'Change Password',
      dd_adminpanel: 'Admin Panel',

      popup_eyebrow: '⚡ Exclusive Welcome Offer',
      popup_title_html: 'Welcome to <span>{brand}</span>',
      popup_desc_html: "Join India's most trusted gaming platform — trusted by <strong>2.4 million+</strong> players for over <strong>10 years</strong>. Sign up now and we'll add ₹{amt} to your wallet, instantly!",
      popup_bonus_label: 'Added to Your Wallet',
      popup_btn: '🏆 Get My ₹{amt} Now',
      popup_skip: "No thanks, I'll play without a bonus",

      marquee: '⚡ TRUSTED GAMING PLATFORM SINCE 2016   •   🎁 GET ₹{amt} FREE ON SIGNUP   •   🎰 12 IN-HOUSE GAMES LIVE NOW   •   💰 INSTANT WITHDRAWALS   •   🏆 10 YEARS OF GAMING EXCELLENCE   •   🎁 JOIN 2.4M+ WINNERS TODAY',

      trust_ssl: 'SSL Secured Platform',
      trust_upi: 'Instant UPI Withdrawals',
      trust_support: '24/7 Live Support',
      trust_rng: 'RNG Certified Fair Play',
      trust_18: '18+ Responsible Gaming',

      hero_eyebrow: 'Live Now — 24,318 Players Online',
      hero_title_html: 'Play Big.<br>Win <span>Bigger.</span>',
      hero_desc: "Card games, live casino and slot games on one platform. Trusted by millions since 2016. Fast KYC, instant payouts, and odds that don't hide the fine print.",
      hero_cta_bonus: 'Get ₹{amt} Free',
      hero_cta_explore: 'Explore Games',
      hero_stat_users_label: 'Registered Users',
      hero_stat_payout_label: 'Paid Out Monthly',
      hero_stat_years_label: 'In Gaming',

      jackpot_tag: "Today's Jackpot",
      jackpot_sub: 'Growing every second · Next draw in 02:14:36',
      jackpot_spin_btn: 'Spin & Try Your Luck',
      jackpot_join_btn: 'Join Now & Play',

      sec_games_eyebrow: '🎮 Game Categories',
      sec_games_title: 'Pick Your Game',
      sec_games_desc: 'From classic card games to live casino action — find your perfect game and start winning today.',
      cat_cards_badge: 'Hot',
      cat_cards_title: 'Card Games',
      cat_cards_desc: 'Teen Patti, Rummy, Poker, Andar Bahar & more classic Indian card games.',
      cat_cards_cnt: '▶ 5 Games Available',
      cat_casino_badge: 'Live',
      cat_casino_title: 'Casino',
      cat_casino_desc: 'Slots, Blackjack, Baccarat, Roulette — Vegas-style thrills at your fingertips.',
      cat_casino_cnt: '▶ 6 Games Available',
      cat_table_badge: 'New',
      cat_table_title: 'Table & Board',
      cat_table_desc: 'Dice Roll, Sic Bo — fast games with instant results.',
      cat_table_cnt: '▶ 2 Games Available',

      allgames_eyebrow: '🎮 Complete Game Library',
      allgames_title: 'All Games',
      allgames_desc: 'Explore our full collection of betting & gaming titles. Click any game to play now.',
      filter_all: 'All Games',
      filter_cards: '🃏 Card Games',
      filter_casino: '🎰 Casino',
      filter_table: '♟ Table & Board',
      game_play_now: 'Play Now',
      game_badge_inhouse: 'Play In-House',

      promo_eyebrow: '🎁 New Player Offer',
      promo_title: 'New Player Welcome Bonus',
      promo_desc: "Sign up today and we'll add ₹{amt} to your wallet instantly — no deposit needed, no wagering requirements. Just play and win.",
      promo_btn: 'Get ₹{amt} Now',
      promo_badge_pct: '₹{amt}',
      promo_badge_label: 'Welcome Credit',
      promo_badge_sub: 'Added instantly on signup',

      how_eyebrow: '▶ 3 Simple Steps',
      how_title: 'How It Works',
      how_desc: 'Getting started on {brand} is quick, easy, and completely free.',
      step1_title: 'Create Account',
      step1_desc: 'Sign up in under 60 seconds with your name, email and mobile number. No documents needed to start.',
      step2_title: 'Add Money',
      step2_desc: 'Deposit via UPI, Net Banking or Card. Instant credit to your {brand} wallet. Minimum deposit just ₹100.',
      step3_title: 'Play & Win',
      step3_desc: 'Choose your game, place your bet and win. Withdraw winnings instantly back to your bank account.',

      wins_eyebrow: '🏆 Recent Big Wins',
      wins_title: "Today's Winners",
      wins_desc: 'Real players, real winnings — updated live every minute.',
      wins_col_player: 'Player',
      wins_col_game: 'Game',
      wins_col_amount: 'Amount Won',
      wins_col_device: 'Device',

      contact_eyebrow: '💬 Get In Touch',
      contact_title: 'Contact Us',
      contact_desc: "Questions, issues with a deposit or withdrawal, or anything else — send us a message and we'll get back to you.",
      label_name: 'Name',
      label_email: 'Email',
      label_subject: 'Subject',
      placeholder_subject: 'e.g. Withdrawal query, account issue...',
      label_message: 'Message',
      btn_send: 'Send Message',
      sending_text: 'Sending...',
      logging_in_text: 'Logging In...',
      creating_account_text: 'Creating Account...',

      foot_desc: "India's most trusted online gaming platform since 2016. Licensed, RNG-certified and committed to responsible gaming for 2.4 million+ players.",
      foot_since: '🏆 Est. 2016',
      foot_header_games: 'Games',
      foot_link_cardgames: 'Card Games',
      foot_link_casinogames: 'Casino Games',
      foot_link_tablegames: 'Table Games',
      foot_link_allgames: 'All Games',
      foot_header_account: 'Account',
      foot_link_signup: 'Sign Up',
      foot_link_login: 'Log In',
      foot_header_support: 'Support',
      foot_link_help: 'Help Centre',
      foot_link_responsible: 'Responsible Gaming',
      foot_link_privacy: 'Privacy Policy',
      foot_link_terms: 'Terms & Conditions',
      foot_link_contactus: 'Contact Us',
      foot_disclaimer: '🔞 18+ only. Gambling can be addictive. Play responsibly. This platform is for entertainment purposes only.',
      foot_age_badge: '18+ Only',
      foot_ssl_badge: '🔒 SSL Secured',
    },

    hi: {
      nav_games: 'गेम्स',
      nav_all_games: 'सभी गेम्स',
      nav_promotions: 'ऑफर्स',
      nav_how: 'कैसे खेलें',
      nav_contact: 'संपर्क करें',
      nav_home: 'होम',
      btn_login: 'लॉग इन',
      btn_joinnow: 'अभी जुड़ें',
      btn_logout: 'लॉग आउट',
      dd_addmoney: 'पैसे जोड़ें',
      dd_mywallet: 'मेरा वॉलेट',
      dd_editprofile: 'प्रोफ़ाइल संपादित करें',
      dd_changepassword: 'पासवर्ड बदलें',
      dd_adminpanel: 'एडमिन पैनल',

      popup_eyebrow: '⚡ विशेष स्वागत ऑफर',
      popup_title_html: '<span>{brand}</span> में आपका स्वागत है',
      popup_desc_html: 'भारत के सबसे भरोसेमंद गेमिंग प्लेटफ़ॉर्म से जुड़ें — <strong>2.4 करोड़+</strong> खिलाड़ियों का भरोसा, पिछले <strong>10 सालों</strong> से। अभी साइन अप करें और हम आपके वॉलेट में तुरंत ₹{amt} जोड़ देंगे!',
      popup_bonus_label: 'आपके वॉलेट में जोड़ा गया',
      popup_btn: '🏆 अभी मेरे ₹{amt} पाएं',
      popup_skip: 'नहीं धन्यवाद, मैं बिना बोनस के खेलूँगा',

      marquee: '⚡ 2016 से भरोसेमंद गेमिंग प्लेटफ़ॉर्म   •   🎁 साइन अप पर ₹{amt} मुफ़्त पाएं   •   🎰 12 इन-हाउस गेम्स लाइव   •   💰 तुरंत निकासी   •   🏆 10 साल की गेमिंग उत्कृष्टता   •   🎁 24 लाख+ विजेताओं से जुड़ें',

      trust_ssl: 'SSL सुरक्षित प्लेटफ़ॉर्म',
      trust_upi: 'तुरंत UPI निकासी',
      trust_support: '24/7 लाइव सहायता',
      trust_rng: 'RNG प्रमाणित फेयर प्ले',
      trust_18: '18+ जिम्मेदार गेमिंग',

      hero_eyebrow: 'अभी लाइव — 24,318 खिलाड़ी ऑनलाइन',
      hero_title_html: 'बड़ा खेलो.<br>बड़ा <span>जीतो.</span>',
      hero_desc: 'कार्ड गेम्स, लाइव कैसीनो और स्लॉट गेम्स एक ही प्लेटफ़ॉर्म पर। 2016 से लाखों लोगों का भरोसा। तेज़ KYC, तुरंत भुगतान, और बिना छिपी शर्तों वाली सही ऑड्स।',
      hero_cta_bonus: '₹{amt} मुफ़्त पाएं',
      hero_cta_explore: 'गेम्स देखें',
      hero_stat_users_label: 'पंजीकृत उपयोगकर्ता',
      hero_stat_payout_label: 'मासिक भुगतान',
      hero_stat_years_label: 'गेमिंग में वर्ष',

      jackpot_tag: 'आज का जैकपॉट',
      jackpot_sub: 'हर सेकंड बढ़ रहा है · अगला ड्रॉ 02:14:36 में',
      jackpot_spin_btn: 'स्पिन करें और किस्मत आज़माएं',
      jackpot_join_btn: 'अभी जुड़ें और खेलें',

      sec_games_eyebrow: '🎮 गेम श्रेणियाँ',
      sec_games_title: 'अपना गेम चुनें',
      sec_games_desc: 'क्लासिक कार्ड गेम्स से लेकर लाइव कैसीनो एक्शन तक — अपना पसंदीदा गेम खोजें और आज ही जीतना शुरू करें।',
      cat_cards_badge: 'हॉट',
      cat_cards_title: 'कार्ड गेम्स',
      cat_cards_desc: 'तीन पत्ती, रम्मी, पोकर, अंदर बाहर और अन्य क्लासिक भारतीय कार्ड गेम्स।',
      cat_cards_cnt: '▶ 5 गेम्स उपलब्ध',
      cat_casino_badge: 'लाइव',
      cat_casino_title: 'कैसीनो',
      cat_casino_desc: 'स्लॉट्स, ब्लैकजैक, बकारा, रूलेट — वेगास-स्टाइल रोमांच आपकी उंगलियों पर।',
      cat_casino_cnt: '▶ 6 गेम्स उपलब्ध',
      cat_table_badge: 'नया',
      cat_table_title: 'टेबल और बोर्ड',
      cat_table_desc: 'डाइस रोल, सिक बो — तुरंत नतीजों वाले तेज़ गेम्स।',
      cat_table_cnt: '▶ 2 गेम्स उपलब्ध',

      allgames_eyebrow: '🎮 पूरी गेम लाइब्रेरी',
      allgames_title: 'सभी गेम्स',
      allgames_desc: 'हमारे बेटिंग और गेमिंग टाइटल्स का पूरा संग्रह देखें। अभी खेलने के लिए कोई भी गेम चुनें।',
      filter_all: 'सभी गेम्स',
      filter_cards: '🃏 कार्ड गेम्स',
      filter_casino: '🎰 कैसीनो',
      filter_table: '♟ टेबल और बोर्ड',
      game_play_now: 'अभी खेलें',
      game_badge_inhouse: 'इन-हाउस गेम',

      promo_eyebrow: '🎁 नए खिलाड़ी का ऑफर',
      promo_title: 'नए खिलाड़ी का स्वागत बोनस',
      promo_desc: 'आज ही साइन अप करें और हम तुरंत आपके वॉलेट में ₹{amt} जोड़ देंगे — न कोई डिपॉज़िट, न कोई शर्त। बस खेलें और जीतें।',
      promo_btn: '₹{amt} अभी पाएं',
      promo_badge_pct: '₹{amt}',
      promo_badge_label: 'स्वागत क्रेडिट',
      promo_badge_sub: 'साइन अप पर तुरंत जोड़ा गया',

      how_eyebrow: '▶ 3 आसान चरण',
      how_title: 'कैसे खेलें',
      how_desc: '{brand} पर शुरुआत करना तेज़, आसान और पूरी तरह मुफ़्त है।',
      step1_title: 'खाता बनाएं',
      step1_desc: 'अपने नाम, ईमेल और मोबाइल नंबर के साथ 60 सेकंड से भी कम समय में साइन अप करें। शुरू करने के लिए किसी दस्तावेज़ की ज़रूरत नहीं।',
      step2_title: 'पैसे जोड़ें',
      step2_desc: 'UPI, नेट बैंकिंग या कार्ड से जमा करें। आपके {brand} वॉलेट में तुरंत क्रेडिट। न्यूनतम जमा सिर्फ़ ₹100।',
      step3_title: 'खेलें और जीतें',
      step3_desc: 'अपना गेम चुनें, बेट लगाएं और जीतें। जीत की राशि तुरंत अपने बैंक खाते में निकालें।',

      wins_eyebrow: '🏆 हाल की बड़ी जीत',
      wins_title: 'आज के विजेता',
      wins_desc: 'असली खिलाड़ी, असली जीत — हर मिनट लाइव अपडेट।',
      wins_col_player: 'खिलाड़ी',
      wins_col_game: 'गेम',
      wins_col_amount: 'जीती गई राशि',
      wins_col_device: 'डिवाइस',

      contact_eyebrow: '💬 संपर्क करें',
      contact_title: 'संपर्क करें',
      contact_desc: 'सवाल, डिपॉज़िट या निकासी से जुड़ी कोई समस्या, या कुछ और — हमें संदेश भेजें, हम जल्द जवाब देंगे।',
      label_name: 'नाम',
      label_email: 'ईमेल',
      label_subject: 'विषय',
      placeholder_subject: 'जैसे — निकासी से जुड़ा सवाल, खाता समस्या...',
      label_message: 'संदेश',
      btn_send: 'संदेश भेजें',
      sending_text: 'भेजा जा रहा है...',
      logging_in_text: 'लॉग इन हो रहा है...',
      creating_account_text: 'खाता बनाया जा रहा है...',

      foot_desc: '2016 से भारत का सबसे भरोसेमंद ऑनलाइन गेमिंग प्लेटफ़ॉर्म। लाइसेंस प्राप्त, RNG-प्रमाणित और 24 लाख+ खिलाड़ियों के लिए जिम्मेदार गेमिंग के प्रति प्रतिबद्ध।',
      foot_since: '🏆 स्थापित 2016',
      foot_header_games: 'गेम्स',
      foot_link_cardgames: 'कार्ड गेम्स',
      foot_link_casinogames: 'कैसीनो गेम्स',
      foot_link_tablegames: 'टेबल गेम्स',
      foot_link_allgames: 'सभी गेम्स',
      foot_header_account: 'खाता',
      foot_link_signup: 'साइन अप',
      foot_link_login: 'लॉग इन',
      foot_header_support: 'सहायता',
      foot_link_help: 'सहायता केंद्र',
      foot_link_responsible: 'जिम्मेदार गेमिंग',
      foot_link_privacy: 'गोपनीयता नीति',
      foot_link_terms: 'नियम व शर्तें',
      foot_link_contactus: 'संपर्क करें',
      foot_disclaimer: '🔞 केवल 18+। जुआ लत लगा सकता है। जिम्मेदारी से खेलें। यह प्लेटफ़ॉर्म केवल मनोरंजन के लिए है।',
      foot_age_badge: '18+ केवल',
      foot_ssl_badge: '🔒 SSL सुरक्षित',
    },

    hinglish: {
      nav_games: 'Games',
      nav_all_games: 'All Games',
      nav_promotions: 'Offers',
      nav_how: 'Kaise Khelein',
      nav_contact: 'Contact Karein',
      nav_home: 'Home',
      btn_login: 'Login Karo',
      btn_joinnow: 'Abhi Judo',
      btn_logout: 'Logout',
      dd_addmoney: 'Paise Add Karo',
      dd_mywallet: 'Mera Wallet',
      dd_editprofile: 'Profile Edit Karo',
      dd_changepassword: 'Password Badlo',
      dd_adminpanel: 'Admin Panel',

      popup_eyebrow: '⚡ Special Welcome Offer',
      popup_title_html: '<span>{brand}</span> Mein Aapka Swagat Hai',
      popup_desc_html: "India ke sabse trusted gaming platform se judein — <strong>2.4 million+</strong> players ka bharosa, pichle <strong>10 saalon</strong> se. Abhi sign up karo aur hum aapke wallet mein turant ₹{amt} add kar denge!",
      popup_bonus_label: 'Wallet Mein Add Ho Gaya',
      popup_btn: '🏆 Abhi Mere ₹{amt} Lo',
      popup_skip: 'Nahi shukriya, main bina bonus ke khelunga',

      marquee: '⚡ 2016 SE TRUSTED GAMING PLATFORM   •   🎁 SIGNUP PAR ₹{amt} FREE PAO   •   🎰 12 IN-HOUSE GAMES LIVE   •   💰 INSTANT WITHDRAWAL   •   🏆 10 SAAL KI GAMING EXCELLENCE   •   🎁 24 LAKH+ WINNERS SE JUDO',

      trust_ssl: 'SSL Secured Platform',
      trust_upi: 'Instant UPI Withdrawal',
      trust_support: '24/7 Live Support',
      trust_rng: 'RNG Certified Fair Play',
      trust_18: '18+ Responsible Gaming',

      hero_eyebrow: 'Abhi Live — 24,318 Players Online',
      hero_title_html: 'Bada Khelo.<br>Bada <span>Jeeto.</span>',
      hero_desc: "Card games, live casino aur slot games — sab ek hi platform par. 2016 se lakhon logon ka bharosa. Fast KYC, instant payout, aur odds jo chhupti nahi.",
      hero_cta_bonus: '₹{amt} Free Pao',
      hero_cta_explore: 'Games Dekho',
      hero_stat_users_label: 'Registered Users',
      hero_stat_payout_label: 'Monthly Payout',
      hero_stat_years_label: 'Gaming Mein Saal',

      jackpot_tag: "Aaj Ka Jackpot",
      jackpot_sub: 'Har second badh raha hai · Agla draw 02:14:36 mein',
      jackpot_spin_btn: 'Spin Karo, Kismat Aazmao',
      jackpot_join_btn: 'Abhi Judo Aur Khelo',

      sec_games_eyebrow: '🎮 Game Categories',
      sec_games_title: 'Apna Game Chuno',
      sec_games_desc: 'Classic card games se lekar live casino action tak — apna favourite game dhundo aur aaj hi jeetna shuru karo.',
      cat_cards_badge: 'Hot',
      cat_cards_title: 'Card Games',
      cat_cards_desc: 'Teen Patti, Rummy, Poker, Andar Bahar aur bhi classic Indian card games.',
      cat_cards_cnt: '▶ 5 Games Available',
      cat_casino_badge: 'Live',
      cat_casino_title: 'Casino',
      cat_casino_desc: 'Slots, Blackjack, Baccarat, Roulette — Vegas-style thrill, aapki ungliyon par.',
      cat_casino_cnt: '▶ 6 Games Available',
      cat_table_badge: 'New',
      cat_table_title: 'Table Aur Board',
      cat_table_desc: 'Dice Roll, Sic Bo — instant result wale fast games.',
      cat_table_cnt: '▶ 2 Games Available',

      allgames_eyebrow: '🎮 Poori Game Library',
      allgames_title: 'All Games',
      allgames_desc: 'Hamare betting aur gaming titles ka pura collection dekho. Abhi khelne ke liye koi bhi game click karo.',
      filter_all: 'All Games',
      filter_cards: '🃏 Card Games',
      filter_casino: '🎰 Casino',
      filter_table: '♟ Table Aur Board',
      game_play_now: 'Abhi Khelo',
      game_badge_inhouse: 'In-House Game',

      promo_eyebrow: '🎁 New Player Offer',
      promo_title: 'New Player Welcome Bonus',
      promo_desc: "Aaj hi sign up karo aur hum turant aapke wallet mein ₹{amt} add kar denge — na koi deposit, na koi wagering. Bas khelo aur jeeto.",
      promo_btn: '₹{amt} Abhi Pao',
      promo_badge_pct: '₹{amt}',
      promo_badge_label: 'Welcome Credit',
      promo_badge_sub: 'Signup par turant add hota hai',

      how_eyebrow: '▶ 3 Aasaan Steps',
      how_title: 'Kaise Khelein',
      how_desc: '{brand} par shuruaat karna fast, easy aur bilkul free hai.',
      step1_title: 'Account Banao',
      step1_desc: 'Apne naam, email aur mobile number ke saath 60 second se bhi kam time mein sign up karo. Shuru karne ke liye kisi document ki zaroorat nahi.',
      step2_title: 'Paise Add Karo',
      step2_desc: 'UPI, Net Banking ya Card se deposit karo. Aapke {brand} wallet mein instant credit. Minimum deposit sirf ₹100.',
      step3_title: 'Khelo Aur Jeeto',
      step3_desc: 'Apna game chuno, bet lagao aur jeeto. Jeeti hui rakam turant apne bank account mein withdraw karo.',

      wins_eyebrow: '🏆 Recent Big Wins',
      wins_title: 'Aaj Ke Winners',
      wins_desc: 'Real players, real winnings — har minute live update.',
      wins_col_player: 'Player',
      wins_col_game: 'Game',
      wins_col_amount: 'Jeeti Rakam',
      wins_col_device: 'Device',

      contact_eyebrow: '💬 Contact Karein',
      contact_title: 'Contact Us',
      contact_desc: "Sawaal, deposit ya withdrawal ki koi problem, ya kuch aur — humein message bhejo, hum jaldi reply karenge.",
      label_name: 'Naam',
      label_email: 'Email',
      label_subject: 'Subject',
      placeholder_subject: 'jaise — withdrawal query, account issue...',
      label_message: 'Message',
      btn_send: 'Message Bhejo',
      sending_text: 'Bheja ja raha hai...',
      logging_in_text: 'Login ho raha hai...',
      creating_account_text: 'Account ban raha hai...',

      foot_desc: "2016 se India ka sabse trusted online gaming platform. Licensed, RNG-certified aur 24 lakh+ players ke liye responsible gaming ke liye committed.",
      foot_since: '🏆 Est. 2016',
      foot_header_games: 'Games',
      foot_link_cardgames: 'Card Games',
      foot_link_casinogames: 'Casino Games',
      foot_link_tablegames: 'Table Games',
      foot_link_allgames: 'All Games',
      foot_header_account: 'Account',
      foot_link_signup: 'Sign Up',
      foot_link_login: 'Log In',
      foot_header_support: 'Support',
      foot_link_help: 'Help Centre',
      foot_link_responsible: 'Responsible Gaming',
      foot_link_privacy: 'Privacy Policy',
      foot_link_terms: 'Terms & Conditions',
      foot_link_contactus: 'Contact Us',
      foot_disclaimer: '🔞 Sirf 18+. Gambling addictive ho sakta hai. Responsibly khelein. Yeh platform sirf entertainment ke liye hai.',
      foot_age_badge: '18+ Only',
      foot_ssl_badge: '🔒 SSL Secured',
    },
  };

  var STORAGE_KEY = 'ds_lang';
  var LANG_NAMES = { en: 'EN', hi: 'हिं', hinglish: 'Hinglish' };
  var currentLang = 'en';

  function getBonusAmount() {
    return document.body.getAttribute('data-bonus') || '20';
  }

  function getBrandName() {
    return document.body.getAttribute('data-brand') || 'Darkshadow';
  }

  function resolve(lang, key) {
    var dict = DS_I18N[lang] || DS_I18N.en;
    var str = dict[key];
    if (str === undefined) str = DS_I18N.en[key];
    if (str === undefined) return null;
    return str.replace(/\{amt\}/g, getBonusAmount()).replace(/\{brand\}/g, getBrandName());
  }

  function applyLanguage(lang) {
    if (!DS_I18N[lang]) lang = 'en';
    currentLang = lang;
    document.documentElement.setAttribute('lang', lang === 'hi' ? 'hi' : 'en');

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var val = resolve(lang, el.getAttribute('data-i18n'));
      if (val !== null) el.textContent = val;
    });
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var val = resolve(lang, el.getAttribute('data-i18n-html'));
      if (val !== null) el.innerHTML = val;
    });
    document.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
      var val = resolve(lang, el.getAttribute('data-i18n-ph'));
      if (val !== null) el.setAttribute('placeholder', val);
    });

    document.querySelectorAll('.lang-switch-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });

    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }

  function setLanguage(lang) {
    applyLanguage(lang);
  }
  window.dsSetLanguage = setLanguage;
  // Lets other inline scripts (e.g. a form's "Sending..." button state) pull
  // a one-off translated string in the currently active language.
  window.dsT = function (key) { return resolve(currentLang, key); };

  document.addEventListener('DOMContentLoaded', function () {
    var saved = 'en';
    try { saved = localStorage.getItem(STORAGE_KEY) || 'en'; } catch (e) {}
    applyLanguage(saved);

    document.querySelectorAll('.lang-switch-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        setLanguage(btn.getAttribute('data-lang'));
      });
    });
  });
})();
