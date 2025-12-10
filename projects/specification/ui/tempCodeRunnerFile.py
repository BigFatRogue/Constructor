        self.widget_content = WidgetContent(self)
        self.widget_content.signal_status.connect(self.set_status)
        self.widget_content.page_property_projcet.signal_save_project.connect(self.save_project)
        self.widget_browser.signal_del_item.connect(self.widget_content.view_empty_page)