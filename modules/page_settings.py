# -*- coding: utf-8 -*-
"""
وحدة إعدادات الصفحات - تحتوي على إعدادات كل صفحة في التطبيق
"""

# إعدادات صفحة دمج وطباعة
merge_print_settings = {
    "page_name": "دمج وطباعة",
    "accepted_file_types": [".pdf"],
    "max_files": None,  # لا يوجد حد أقصى لعدد الملفات
    "allow_folders": True,  # يسمح إسقاط مجلدات
    "allow_sequential_drops": True,  # السماح بإضافة ملفات واحدًا تلو الآخر
    "description": "واجهة دمج وطباعة ملفات PDF"
}

# إعدادات صفحة التقسيم
split_settings = {
    "page_name": "تقسيم",
    "accepted_file_types": [".pdf"],
    "max_files": 1,  # ملف واحد فقط في كل مرة
    "allow_folders": False,  # لا يسمح بإسقاط مجلدات
    "allow_sequential_drops": True,  # السماح بإضافة ملفات واحدًا تلو الآخر
    "description": "واجهة تقسيم ملفات PDF"
}

# إعدادات صفحة الضغط
compress_settings = {
    "page_name": "ضغط",
    "accepted_file_types": [".pdf"],
    "max_files": None,  # يمكن تحديده لاحقًا
    "allow_folders": "dynamic",  # يعتمد على حالة checkbox
    "description": "واجهة ضغط ملفات PDF",
    "allow_sequential_drops": True,  # السماح بإضافة ملفات واحدًا تلو الآخر
    "folder_option": "checkbox"  # تحديد أن خيار المجلد يعتمد على checkbox
}

# إعدادات صفحة الختم والتدوير
stamp_rotate_settings = {
    "page_name": "ختم وتدوير",
    "accepted_file_types": [".pdf"],
    "max_files": 1,  # ملف واحد فقط في كل مرة
    "allow_folders": False,  # لا يسمح بإسقاط مجلدات
    "allow_sequential_drops": True,  # السماح بإضافة ملفات واحدًا تلو الآخر
    "description": "واجهة ختم وتدوير ملفات PDF"
}

# إعدادات صفحة الحماية والخصائص
protect_properties_settings = {
    "page_name": "حماية وخصائص",
    "accepted_file_types": [".pdf"],
    "max_files": 1,  # ملف واحد فقط في كل مرة
    "allow_folders": False,  # لا يسمح بإسقاط مجلدات
    "allow_sequential_drops": True,  # السماح بإضافة ملفات واحدًا تلو الآخر
    "description": "واجهة حماية وخصائص ملفات PDF"
}

# إعدادات صفحة التحويل
convert_settings = {
    "page_name": "تحويل",
    "accepted_file_types": [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".txt", ".doc", ".docx"],  # أنواع الملفات المسموحة
    "max_files": None,  # يمكن تحديده لاحقًا
    "allow_folders": False,  # لا يسمح بإسقاط مجلدات
    "description": "واجهة تحويل الملفات",
    "dynamic_file_types": True,  # تحديد أن أنواع الملفات تعتمد على التبويب النشط
    "allow_sequential_drops": True,  # السماح بإضافة ملفات واحدًا تلو الآخر
    "tab_dependent": True  # تحديد أن قبول الملفات يعتمد على التبويب المحدد
}

# قاموس يجمع كل إعدادات الصفحات
page_settings = {
    "merge_print": merge_print_settings,
    "split": split_settings,
    "compress": compress_settings,
    "stamp_rotate": stamp_rotate_settings,
    "protect_properties": protect_properties_settings,
    "convert": convert_settings
}
