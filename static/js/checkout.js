$(document).ready(function () {

  $('#rzp-button1').click(function (e){
    e.preventDefault();

    // taking all the required fields of checkout

    var first_name=$("[name='first_name']").val()
    var last_name=$("[name='last_name']").val()
    var email=$("[name='email']").val()
    var phone=$("[name='phone']").val()
    var address_line_1=$("[name='address_line_1']").val()
    var address_line_2=$("[name='address_line_2']").val()
    var city=$("[name='city']").val()
    var state=$("[name='state']").val()
    var country=$("[name='country']").val()
    var order_note=$("[name='order_note']").val()

    var options = {
    "key": "YOUR_KEY_ID", // Enter the Key ID generated from the Dashboard
    "amount": "50000", // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
    "currency": "INR",
    "name": "Acme Corp",
    "description": "Test Transaction",
    "image": "https://example.com/your_logo",
    "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
    "handler": function (response){
        alert(response.razorpay_payment_id);
        alert(response.razorpay_order_id);
        alert(response.razorpay_signature)
    },
    "prefill": {
        "name": "Gaurav Kumar",
        "email": "gaurav.kumar@example.com",
        "contact": "9999999999"
    },
    "notes": {
        "address": "Razorpay Corporate Office"
    },
    "theme": {
        "color": "#3399cc"
    }
};
var rzp1 = new Razorpay(options);
rzp1.on('payment.failed', function (response){
        alert(response.error.code);
        alert(response.error.description);
        alert(response.error.source);
        alert(response.error.step);
        alert(response.error.reason);
        alert(response.error.metadata.order_id);
        alert(response.error.metadata.payment_id);
});
    rzp1.open();
  })

})
