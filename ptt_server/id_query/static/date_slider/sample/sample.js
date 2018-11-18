;(function() {
    "use strict";

    function dateFormat(date, fmt) {
        var o = {
            "M+": date.getMonth() + 1,
            "d+": date.getDate(),
        };
        if (/(y+)/.test(fmt)){
            fmt = fmt.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length));
        }
        for (var k in o) {
            if (new RegExp("(" + k + ")").test(fmt)){
                fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
            }
        }
        return fmt;
    }

    var startDate = new Date("2013/11/12"),
        endDate = new Date("2016/12/22"),
        offset = endDate - startDate;

    var counter = 0;
    var firstIn_flag = 1;
    var counterForflag = 0;

    window.hello = $("#double_date_range").rangepicker({
        type: "double",
        startValue: dateFormat(startDate, "yyyy/MM/dd"),
        endValue: dateFormat(endDate, "yyyy/MM/dd"),
        translateSelectLabel: function(currentPosition, totalPosition) {
            var timeOffset = offset * ( currentPosition / totalPosition);
            var date = new Date(+startDate + parseInt(timeOffset));

            counterForflag = counterForflag + 1;
            if(counterForflag <= 4 && firstIn_flag == 1){
                Global_endDate = dateFormat(endDate, "yyyy/MM/dd");
                Global_startDate = dateFormat(startDate, "yyyy/MM/dd"),
                console.log(Global_endDate);
                console.log(Global_startDate);

                firstIn_flag = 0;
            }
            else if(counterForflag > 4 && firstIn_flag == 0){
                counter = counter + 1;
                if(counter == 1){
                    Global_endDate = dateFormat(date, "yyyy/MM/dd");
                    console.log(Global_endDate);
                }
                else if(counter == 2){
                    Global_startDate = dateFormat(date, "yyyy/MM/dd");
                    console.log(Global_startDate);
                    counter = 0;            
                }
            }

            return dateFormat(date, "yyyy/MM/dd");
        }
    });

}());
