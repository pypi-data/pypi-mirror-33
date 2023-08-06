# coding=utf-8
from django.forms import Widget, forms
from django.utils.safestring import mark_safe
from django.utils.html import escapejs
from django.conf import settings


class UMEditor(Widget):
    scheme = 'default'
    toolbar = 'mini'

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.update(style="display: none")
        attrs['height'] = attrs.get('height', '100')
        attrs['rel'] = 'kind'
        if attrs and 'scheme' in attrs:
            self.scheme = attrs['scheme']
        if attrs and 'toolbar' in attrs:
            self.toolbar = attrs['toolbar']
        if 'width' in attrs:
            attrs['minFrameWidth'] = attrs['width']
        if 'height' in attrs:
            attrs['minFrameHeight'] = attrs['height']
        super(UMEditor, self).__init__(attrs)

    editorBasePath = '%s%s' % (settings.STATIC_URL, 'zui/dist/lib/umeditor/')

    def _media(self):

        css = {'all': ('%s%s' % (self.editorBasePath, 'themes/default/css/umeditor.min.css'),)}

        return forms.Media(js=('%s%s' % (self.editorBasePath, 'umeditor.config.js'),
                               '%s%s' % (self.editorBasePath, 'umeditor.min.js'),
                               '%s%s' % (self.editorBasePath, 'lang/zh-cn/zh-cn.js'),
                               ),
                           css=css
                           )

    media = property(_media)

    def _get_toolbar_items(self):
        if self.toolbar == 'mini':
            return """
            ,toolbar : ['bold italic underline strikethrough removeformat |',
                      'insertorderedlist insertunorderedlist forecolor',
                      'backcolor fontfamily fontsize subscript superscript |',
                      'link unlink emotion formula']
            """
        elif self.toolbar == 'small':
            return """
            ,toolbar: [
                        'cleardoc | bold italic underline strikethrough removeformat', 
                        '| insertorderedlist insertunorderedlist forecolor backcolor', 
                        'fontfamily fontsize subscript superscript | link unlink',
                        'emotion image video formula'
                        ]
            """
        elif self.toolbar == 'tiny':
            return """
            ,toolbar: [
                        'bold italic underline strikethrough removeformat',
                        '| insertorderedlist insertunorderedlist forecolor backcolor',
                        'fontfamily fontsize subscript superscript',
                        'image formula'
                        ]
            """
        else:
            return """
            ,toolbar:[
                'source | undo redo | bold italic underline strikethrough | superscript subscript | forecolor backcolor | removeformat |',
                'insertorderedlist insertunorderedlist | selectall cleardoc paragraph | fontfamily fontsize',
                '| justifyleft justifycenter justifyright justifyjustify |',
                'link unlink | emotion image video  | map',
                '| horizontal print preview  fullscreen', 'drafts', 'formula']
            """

    def _get_umeditor_attrs(self):
        return ''.join((
            ',initialFrameWidth:"%s"' % self.attrs['width'] if 'width' in self.attrs else '',
            ',initialFrameHeight:"%s"' % self.attrs['height'] if 'height' in self.attrs else '',
            ',minFrameWidth:"%s"' % self.attrs['minFrameWidth'] if 'minFrameWidth' in self.attrs else '',
            ',minFrameHeight:"%s"' % self.attrs['minFrameHeight'] if 'minFrameHeight' in self.attrs else '',
            self._get_toolbar_items()
        ))

    def render(self, name, value, attrs=None):
        """
            数学公式格式: <span data-latex="公式元数据"> static html <span>
        """
        textarea = u'''
            <script id="id_{name}" name="{name}" type="text/plain"></script>

            <script type="text/javascript">
            $(document).ready(function(){{

                // 输出规则： static html替换iframe, 元数据保存在data-latex
                function formulaEditToStatic(root){{
                    var um = this;
                    $.each(root.getNodesByTagName('iframe'), function (i, node) {{
                        if (node.hasClass('mathquill-embedded-latex')) {{
                            var formulaEle = $('div.main', $(um.body).find('iframe')[i].contentWindow.document);
                            if (formulaEle.length == 0) return ;

                            var formulaHtml = $.trim(formulaEle.html());
                            var formulaNode = UM.htmlparser(formulaHtml);
                            var formulaFirChild = formulaNode.firstChild();

                            formulaFirChild.tagName = 'span';
                            formulaFirChild.setAttr('data-latex', node.getAttr('data-latex'));
                            formulaFirChild.removeClass("mathquill-editable");

                            node.parentNode.replaceChild(formulaNode, node);
                        }}
                    }});
                }}

                // 输入规则：静态class修改为可编辑class，元数据替换标签内容.
                function modifyFormulaInfo(root){{
                    $.each(root.getNodesByTagName('span'), function (i, node) {{
                        if (node.hasClass('mathquill-rendered-math') && node.getAttr('data-latex')) {{
                            node.addClass('mathquill-embedded-latex');
                            node.innerHTML(node.getAttr('data-latex'));
                        }}
                    }});
                }}

                if (!UM.customFormulaReady){{

                    var originFormulaPlugin = UM.plugins['formula'];
                    UM.plugins['formula'] = function () {{
                        this.addOutputRule(formulaEditToStatic);
                        this.addInputRule(modifyFormulaInfo);
                        originFormulaPlugin.call(this);
                    }};

                    // formula 添加 π、↑, 转义"<"为"&lt;"
                    var originRegisterWidget = UM.registerWidget;
                    UM.registerWidget = function(name,pro,cb){{
                        if (name === "formula"){{
                            pro.sourceData.formula.letter.push('{{/}}pi');
                            pro.sourceData.formula.symbol.push('↑');
                            var originInsertLatex = pro.insertLatex;
                            pro.insertLatex = function (latex) {{
                                latex === "<" && (latex = "&lt;");
                                originInsertLatex.call(pro, latex);
                            }}
                        }}
                        originRegisterWidget(name, pro, cb);
                    }}

                    UM.customFormulaReady = true;
                }}

                var um = UM.getEditor('id_{name}',
                    {{
                        UMEDITOR_HOME_URL: "/static/zui/dist/lib/umeditor/",
                        theme: '{theme}'
                        {style},
                        imageUrl: '{upload_url}',
                        imagePath: "",
                        autoHeightEnabled: true,
                        imageFieldName: 'imgFile',
                        autoClearinitialContent: false, //自动清除编辑器初始内容会直接附值，跳过setcontent中的inputrule
                        initialStyle: 'p{{font-size: 13px}}',
                    }}
                );
                um.setContent('{value}');
                um.addListener('blur selectionchange', function(){{
                    this.sync();
                }});
                // 初始化时，输入规则生成的iframe中的script的执行会慢于自定义输出规则，导致输出规则查找不到相应元素, 等iframe
                // 加载完成再同步
                $('iframe').load(function(){{
                    um.sync();
                }});
            }});
        </script>
        '''.format(name=name, theme=self.scheme,
                   style=self._get_umeditor_attrs(),
                   upload_url="/kind_upload/",
                   value=value and escapejs(value) or u'')
        return mark_safe(textarea)
