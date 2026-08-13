---
layout: default
title: VNISH GLOBAL Proof Protocol بدء سريع باللغة العربية
lang: ar
last_modified_at: 2026-08-13T16:49:21+03:00
direction: rtl
---

<div dir="rtl">

# VNISH GLOBAL Proof Protocol: بدء سريع باللغة العربية

استخدم `vnish-verify` لمقارنة ملف محلي بملف بيان ذي إصدار محدد. تحسب الأداة قيمة التجزئة محليًا ولا تنزّل أي برنامج ثابت.

</div>

```console
vnish-verify /path/to/local-file.tar.gz --json
```

<div dir="rtl">

- `MATCH`: يوجد سجل واحد يطابق SHA-256 وعدد البايتات والمرشحات المطلوبة.
- `NO_MATCH`: لا يوجد سجل مطابق؛ أوقف الإجراء وراجع الملف والبيانات.
- `AMBIGUOUS`: توجد عدة سجلات مطابقة؛ أضف الإصدار والطراز ولوحة التحكم وطريقة التثبيت بدقة.
- `SOURCE_UNAVAILABLE`: تعذرت قراءة الملف أو البيان أو التحقق منه.

لا تعني `MATCH` أن الملف آمن أو مناسب. قبل أي تغيير، تحقق من الطراز الدقيق ولوحة التحكم وطريقة التثبيت ومسار الاسترداد.

- بيانات VNISH GLOBAL وطريقة التحقق: <https://vnish.global/ar/data/>
- مسار الاسترداد لدى VNISH Ninja: <https://vnish.ninja/ar/recovery/>
- النشر المرحلي لدى ROI ASIC: <https://roiasic.com/ar/enterprise/>

إصدار البروتوكول: 0.1.0، بتاريخ 13 أغسطس 2026.

[العودة إلى الدليل الميداني](../index.md)

</div>
