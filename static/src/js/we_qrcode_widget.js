/** @odoo-module */

import {registry} from "@web/core/registry";

const {Component, xml, useEffect, onWillStart} = owl;
import {loadJS} from "@web/core/assets";
import {useService} from "@web/core/utils/hooks";

/**
 * This widget adds a ribbon on the top right side of the form
 *
 *      - You can specify the text with the title prop.
 *      - You can specify the title (tooltip) with the tooltip prop.
 *      - You can specify a background color for the ribbon with the bg_color prop
 *        using bootstrap classes :
 *        (bg-primary, bg-secondary, bg-success, bg-danger, bg-warning, bg-info,
 *        bg-light, bg-dark, bg-white)
 *
 *        If you don't specify the bg_color prop the bg-success class will be used
 *        by default.
 */
class WEQrcode extends Component {
    setup() {
        this.rpc = useService("rpc");

        onWillStart(() => loadJS("http://wwcdn.weixin.qq.com/node/wework/wwopen/js/wwLogin-1.2.7.js"));

        useEffect(async () => {
            // to safety, we can not request by search_read, so we use rpc
            const app = await this.rpc('/we/qrcode', {
                app_id: this.props.appId,
                context: {'aaaaa': 222}
            })

            new WwLogin({
                "id": "wx_reg",
                "appid": app.corp_id,
                "agentid": app.agentid,
                "redirect_uri": encodeURIComponent(`${window.location.origin}/we/qrcode/login/${this.props.appId}`),
            });
        }, () => [])
    }
}

WEQrcode.template = xml`
<div style="width: 500px; height: 500px">
    <div id="wx_reg" style="width: 100%;height: 100%;display: flex;justify-content: center;align-items: center;"></div>
</div>
`;

WEQrcode.defaultProps = {
    appId: "",
};
WEQrcode.extractProps = ({attrs}) => {
    return {
        appId: attrs.app_id,
    };
};

registry.category("view_widgets").add("we_qrcode", WEQrcode);
