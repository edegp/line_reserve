<template>
    <v-app>
        <img
            src="https://media.istockphoto.com/photos/stylish-dinner-picture-id1178092305"
            alt="Restaurant"
            style="width: 100%"
        />
        <div style="color: #555; margin-top: 20px" class="mx-5">
            <span
                style="
                    border-left: 12px solid #16c464;
                    padding: 0 15px;
                    color: #555;
                "
                class="text-h5"
                >{{ $t("delete.title") }}</span
            >
            <ul class="text-body-2 mt-5 mb-16">
                <v-form ref="form" v-model="valid" lazy-validation>
                    <li>
                        <v-text-field
                            label="予約した店名"
                            required
                            v-model="reserveInfo.shopName"
                        ></v-text-field>
                    </li>
                    <li>
                        <v-menu
                            ref="menu"
                            v-model="menu"
                            :close-on-content-click="false"
                            :return-value.sync="reserveInfo.date"
                            transition="scale-transition"
                            offset-y
                            min-width="auto"
                        >
                            <template v-slot:activator="{ on, attrs }">
                                <v-text-field
                                    v-model="reserveInfo.date"
                                    label="予約した日付"
                                    prepend-icon="mdi-calendar"
                                    readonly
                                    v-bind="attrs"
                                    v-on="on"
                                ></v-text-field>
                            </template>
                            <v-date-picker
                                v-model="reserveInfo.date"
                                no-title
                                scrollable
                            >
                                <v-spacer></v-spacer>
                                <v-btn
                                    text
                                    color="primary"
                                    @click="menu = false"
                                >
                                    Cancel
                                </v-btn>
                                <v-btn
                                    text
                                    color="primary"
                                    @click="$refs.menu.save(reserveInfo.date)"
                                >
                                    OK
                                </v-btn>
                            </v-date-picker>
                        </v-menu>
                    </li>
                    <li>
                        <v-menu
                            ref="menu2"
                            v-model="menu2"
                            :close-on-content-click="false"
                            :nudge-right="40"
                            :return-value.sync="reserveInfo.time"
                            transition="scale-transition"
                            offset-y
                            max-width="290px"
                            min-width="290px"
                        >
                            <template v-slot:activator="{ on, attrs }">
                                <v-text-field
                                    v-model="reserveInfo.time"
                                    label="予約した時間"
                                    prepend-icon="mdi-clock-time-four-outline"
                                    readonly
                                    v-bind="attrs"
                                    v-on="on"
                                ></v-text-field>
                            </template>
                            <v-time-picker
                                v-if="menu2"
                                v-model="reserveInfo.time"
                                full-width
                                :allowed-minutes="allowedStep"
                                @click:minute="
                                    $refs.menu2.save(reserveInfo.time)
                                "
                            ></v-time-picker>
                        </v-menu>
                    </li>
                </v-form>
            </ul>
        </div>
        <!-- ボタン -->
        <v-footer fixed style="" class="pa-0" height="60px">
            <v-btn
                class="basket text-h5 font-weight-bold"
                color="#00B900"
                v-on:click="deleteReserve(reserveInfo)"
                style="color: #fff; width: 100%; height: 100%"
            >
                <span v-html="$t('delete.msg001')"></span
                ><v-icon large>keyboard_arrow_right</v-icon>
            </v-btn>
        </v-footer>
    </v-app>
</template>

<script>
/**
 * トップページ
 *
 */
export default {
    layout: "reserve/restaurant",
    // components: {
    //     VueFooter,
    // },
    // async asyncData({ app, store, params }) {return {}}
    head() {
        return {
            title: this.$t("title"),
        };
    },
    data() {
        return {
            reserveInfo: {
                shopName: null,
                date: new Date(
                    Date.now() - new Date().getTimezoneOffset() * 60000
                )
                    .toISOString()
                    .substr(0, 10),
                time: null,
            },
            menu: false,
            menu2: false,
            valid: true,
        };
    },
    methods: {
        allowedStep(m) {
            return m % 30 === 0;
        },
        /**
         * エリア・店舗選択画面へ遷移
         *
         */
        /**
         *
         *          予約削除
         * @param {Object} input 予約入力内容
         * @returns {boolean} 正常・異常終了値
         */
        async deleteReserve(input) {
            const token = this.$store.state.lineUser.token;
            const day = input.date;
            const start = input.time;
            const names = input.shopName;
            try {
                const data = await this.$restaurant.deleteReserve(
                    token,
                    day,
                    start,
                    names
                );
                if (data) {
                    const reservationId = data.reservationId;
                    if (isNaN(reservationId)) {
                        this.reserveDialog = false;
                    } else {
                        this.errorDialogMessage.title =
                            this.$t("calendar.msg016");
                        this.errorDialogMessage.text =
                            this.$t("calendar.msg017");
                        this.errorDialog = true;
                        return false;
                    }
                    const message = {
                        no: reservationId,
                        restaurant: this.restaurant,
                        name: this.$store.state.lineUser.name,
                        day: input.date,
                        start: input.time,
                    };
                    this.$flash.set("message", message);
                    this.$router.push("/restaurant/delete_completed");
                }
            } finally {
                this.$processing.hide();
            }
            return true;
        },
    },
};
</script>

<style scoped>
html,
body {
    margin: 0;
    width: 100%;
    height: 100%;
}
li {
    margin-top: 20px;
}
</style>
