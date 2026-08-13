export type Lang = 'en' | 'te' | 'hi' | 'mr'

const translations: Record<string, Record<Lang, string>> = {
  // Navbar
  'nav.dashboard': { en: 'Dashboard', te: 'డాష్‌బోర్డ్', hi: 'डैशबोर्ड', mr: 'डॅशबोर्ड' },
  'nav.advisory': { en: 'Advisory', te: 'సలహా', hi: 'सलाह', mr: 'सल्ला' },
  'nav.disease': { en: 'Disease', te: 'వ్యాధి', hi: 'रोग', mr: 'रोग' },
  'nav.history': { en: 'History', te: 'చరిత్ర', hi: 'इतिहास', mr: 'इतिहास' },

  // Dashboard
  'dash.welcome': { en: 'Welcome', te: 'స్వాగతం', hi: 'स्वागत', mr: 'स्वागत' },
  'dash.subtitle': { en: 'Your AI-powered agricultural advisory platform', te: 'మీ AI ఆధారిత వ్యవసాయ సలహా వేదిక', hi: 'आपका AI-संचालित कृषि सलाह मंच', mr: 'तुमचे AI-संचालित कृषी सल्ला व्यासपीठ' },
  'dash.weather': { en: "Today's Weather", te: 'నేటి వాతావరణం', hi: 'आज का मौसम', mr: 'आजचे हवामान' },
  'dash.season': { en: 'Current Season', te: 'ప్రస్తుత సీజన్', hi: 'वर्तमान मौसम', mr: 'सध्याचा हंगाम' },
  'dash.recommended': { en: 'Recommended crops for', te: 'సిఫార్సు చేసిన పంటలు', hi: 'अनुशंसित फसलें', mr: 'शिफारस केलेली पिके' },
  'dash.getAdvisory': { en: 'Get Advisory', te: 'సలహా పొందండి', hi: 'सलाह लें', mr: 'सल्ला घ्या' },
  'dash.diseaseScanner': { en: 'Disease Scanner', te: 'వ్యాధి స్కానర్', hi: 'रोग स्कैनर', mr: 'रोग स्कॅनर' },
  'dash.advisoryHistory': { en: 'Advisory History', te: 'సలహా చరిత్ర', hi: 'सलाह इतिहास', mr: 'सल्ला इतिहास' },
  'dash.quickStart': { en: 'Quick Start', te: 'త్వరిత ప్రారంభం', hi: 'त्वरित शुरुआत', mr: 'जलद सुरुवात' },
  'dash.startAdvisory': { en: 'Start Advisory →', te: 'సలహా ప్రారంభించండి →', hi: 'सलाह शुरू करें →', mr: 'सल्ला सुरू करा →' },

  // Advisory page
  'adv.title': { en: 'Get Advisory', te: 'సలహా పొందండి', hi: 'सलाह लें', mr: 'सल्ला घ्या' },
  'adv.location': { en: 'Location', te: 'స్థానం', hi: 'स्थान', mr: 'स्थान' },
  'adv.soilParams': { en: 'Soil Parameters', te: 'నేల పరామితులు', hi: 'मिट्टी पैरामीटर', mr: 'माती मापदंड' },
  'adv.getCrop': { en: '🌾 Get Crop Recommendation', te: '🌾 పంట సిఫార్సు పొందండి', hi: '🌾 फसल सिफारिश लें', mr: '🌾 पीक शिफारस घ्या' },
  'adv.confidence': { en: 'Confidence', te: 'విశ్వాసం', hi: 'विश्वास', mr: 'विश्वास' },
  'adv.chatPlaceholder': { en: 'Type your farming question... (e.g. best crop for Warangal?)', te: 'మీ వ్యవసాయ ప్రశ్న టైప్ చేయండి...', hi: 'अपना कृषि प्रश्न टाइप करें...', mr: 'तुमचा शेती प्रश्न टाइप करा...' },

  // Disease page
  'dis.title': { en: 'Disease Scanner', te: 'వ్యాధి స్కానర్', hi: 'रोग स्कैनर', mr: 'रोग स्कॅनर' },
  'dis.subtitle': { en: 'Upload a photo of your crop leaf for AI-powered disease detection and treatment recommendations.', te: 'AI ఆధారిత వ్యాధి గుర్తింపు కోసం మీ పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి.', hi: 'AI-संचालित रोग पहचान के लिए अपनी फसल के पत्ते की फोटो अपलोड करें।', mr: 'AI-संचालित रोग ओळखीसाठी तुमच्या पिकाच्या पानाचा फोटो अपलोड करा.' },
  'dis.dropImage': { en: 'Drop a leaf image here', te: 'ఆకు చిత్రాన్ని ఇక్కడ వదలండి', hi: 'पत्ती की तस्वीर यहाँ डालें', mr: 'पानाची प्रतिमा येथे टाका' },
  'dis.analyse': { en: 'Analyse Leaf', te: 'ఆకును విశ్లేషించండి', hi: 'पत्ती का विश्लेषण करें', mr: 'पानाचे विश्लेषण करा' },

  // History page
  'hist.title': { en: 'Advisory History', te: 'సలహా చరిత్ర', hi: 'सलाह इतिहास', mr: 'सल्ला इतिहास' },
  'hist.empty': { en: 'No advisories yet. Get your first recommendation!', te: 'ఇంకా సలహాలు లేవు. మీ మొదటి సిఫార్సు పొందండి!', hi: 'अभी तक कोई सलाह नहीं। अपनी पहली सिफारिश लें!', mr: 'अद्याप कोणताही सल्ला नाही. तुमची पहिली शिफारस घ्या!' },

  // Common
  'common.logout': { en: 'Logout', te: 'లాగ్ అవుట్', hi: 'लॉग आउट', mr: 'लॉग आउट' },
  'common.humidity': { en: 'Humidity', te: 'తేమ', hi: 'नमी', mr: 'आर्द्रता' },
  'common.wind': { en: 'Wind speed', te: 'గాలి వేగం', hi: 'हवा की गति', mr: 'वाऱ्याचा वेग' },
  'common.conditions': { en: 'Conditions', te: 'పరిస్థితులు', hi: 'स्थितियाँ', mr: 'परिस्थिती' },
  'common.feelsLike': { en: 'Feels like', te: 'అనిపిస్తుంది', hi: 'महसूस होता है', mr: 'वाटते' },
}

export function t(key: string, lang: Lang = 'en'): string {
  return translations[key]?.[lang] || translations[key]?.en || key
}
