const API="/api";
const $=s=>document.querySelector(s);
const money=n=>"₹"+Number(n||0).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2});
const token=()=>localStorage.getItem("mb_token");
const user=()=>JSON.parse(localStorage.getItem("mb_user")||"null");
const cart=()=>JSON.parse(localStorage.getItem("mb_cart")||"[]");
function setCart(c){localStorage.setItem("mb_cart",JSON.stringify(c));renderNav();}
function toast(msg){const x=$("#toast");if(!x)return;x.textContent=msg;x.style.display="block";setTimeout(()=>x.style.display="none",2400)}
async function api(path,opts={}){
  opts.headers={"Content-Type":"application/json",...(opts.headers||{})};
  if(token())opts.headers.Authorization="Bearer "+token();
  const r=await fetch(API+path,opts); const data=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(data.message||"Something went wrong");
  return data;
}
function renderNav(){
 const u=user(), c=cart().reduce((a,x)=>a+x.quantity,0);
 document.querySelectorAll(".cart-badge").forEach(x=>x.textContent=c);
 const auth=document.querySelector("#authLink"); if(auth)auth.innerHTML=u?`<a href="/static/profile.html">Hi, ${u.name.split(" ")[0]}</a>`:`<a href="/static/login.html">Login</a>`;
 const admin=document.querySelector("#adminLink"); if(admin)admin.innerHTML=u?.role==="admin"?`<a href="/static/admin.html">Admin</a>`:"";
}
function shell(content){
 return `<nav class="nav"><div class="container navin">
 <a class="brand" href="/"><img src="/static/assets/logo.jpg"><span>The Monks Berry</span></a>
 <div class="links"><a href="/">Home</a><a href="/static/shop.html">Shop</a><a href="/#story">Our Story</a><a href="/#quality">Quality</a><span id="adminLink"></span></div>
 <div class="actions"><span id="authLink"></span><a class="iconbtn cart-count" href="/static/cart.html">🛒<b class="cart-badge">0</b></a></div>
 </div></nav>${content}
 <div id="toast" class="toast"></div>
 <footer class="footer"><div class="container footer-grid">
 <div><h3>The Monks Berry</h3><p>From the Himalayas to your wellness. Pure, natural and nutritious rosehip products.</p></div>
 <div><h3>Shop</h3><p><a href="/static/shop.html">All Products</a><br><a href="/static/cart.html">Cart</a><br><a href="/static/profile.html">My Orders</a></p></div>
 <div><h3>Customer Care</h3><p>Shipping & delivery<br>Returns & refunds<br>Contact support</p></div>
 </div><div class="container copyright">© 2026 The Monks Berry. All rights reserved.</div></footer>`;
}
function productCard(p){
 return `<article class="card"><a href="/static/product.html?id=${p.id}"><div class="card-img"><img src="${p.image}" alt="${p.name}"></div></a><div class="card-body">
 <span class="tag">${p.weight||"Rosehip"}</span><h3>${p.name}</h3><p>${p.short_description||""}</p>
 <div class="price"><strong>${money(p.price)}</strong><span class="mrp">${money(p.mrp)}</span><span class="tag">${p.discount}% OFF</span></div>
 <div class="card-actions"><a class="btn outline" href="/static/product.html?id=${p.id}">View</a><button class="btn" onclick="addToCart(${p.id})">Add to cart</button></div>
 </div></article>`;
}
async function addToCart(id){
 const data=await api("/products/"+id);const p=data.product;const c=cart();const found=c.find(x=>x.product_id===p.id);
 if(found)found.quantity=Math.min(found.quantity+1,p.stock);else c.push({product_id:p.id,quantity:1,product:p});
 setCart(c);toast("Added to cart");
}
async function loadHome(){
 const el=$("#app");
 el.innerHTML=shell(`<main>
 <section class="hero"><div class="container hero-grid"><div><div class="eyebrow">From the Himalayas to your wellness</div><h1>Pure rosehip.<br>Pure goodness.</h1><p>Discover carefully prepared rosehip products inspired by the wild Himalayan regions — from pulp to dried berries and fine berry powder.</p><div style="display:flex;gap:10px;margin-top:25px"><a class="btn gold" href="/static/shop.html">Shop collection</a><a class="btn outline" href="#story">Explore story</a></div></div><div class="hero-card"><img src="/static/assets/products/rosehip-wellness.jpg" alt="The Monks Berry Himalayan rosehip"></div></div></section>
 <section class="section"><div class="container"><div class="heading"><div><div class="eyebrow">Our collection</div><h2>Himalayan rosehip products</h2></div><a class="btn outline" href="/static/shop.html">View all</a></div><div id="featured" class="products"></div></div></section>
 <section id="quality" class="section alt"><div class="container"><div class="heading"><div><div class="eyebrow">Why Monks Berry</div><h2>Nature, handled with care</h2></div></div><div class="features"><div class="feature"><div class="emoji">🏔️</div><h3>Wild-harvested</h3><p>Inspired by the pure Himalayan regions shown in the product brochure.</p></div><div class="feature"><div class="emoji">🌿</div><h3>100% natural</h3><p>Product range emphasizes pure ingredients and no unnecessary additives.</p></div><div class="feature"><div class="emoji">❤️</div><h3>Nutrient-rich</h3><p>Rosehip products naturally contain vitamin C and plant compounds.</p></div><div class="feature"><div class="emoji">🛡️</div><h3>Pure & trusted</h3><p>Clear product information, storage guidance and transparent checkout.</p></div></div></div></section>
 <section id="story" class="section"><div class="container"><div class="heading"><div><div class="eyebrow">The nature's timeless gift</div><h2>From fruit to everyday wellness</h2></div></div><div class="card" style="padding:30px"><p class="muted" style="font-size:18px;line-height:1.9;margin:0">Rosehip is a small red fruit formed after the rose flower blooms. The brochure presents it as a source of vitamin C, antioxidants, dietary fibre and other plant compounds. The Monks Berry collection brings that ingredient into convenient formats for drinks, teas, smoothies and food preparations.</p></div></div></section>
 </main>`);
 renderNav(); const data=await api("/products?featured=1");$("#featured").innerHTML=data.products.map(productCard).join("");
}
async function loadShop(){
 $("#app").innerHTML=shell(`<main class="container"><section class="page-head"><div class="eyebrow">The collection</div><h1>Shop Rosehip</h1><p>Choose your preferred format.</p></section><div class="toolbar"><input id="search" class="search" placeholder="Search products..."><select id="sort" class="search" style="max-width:190px"><option value="new">Latest</option><option value="low">Price: Low</option><option value="high">Price: High</option></select></div><div id="products" class="products"></div></main>`);
 renderNav(); const load=async()=>{const q=$("#search").value;let d=await api("/products?q="+encodeURIComponent(q));if($("#sort").value==="low")d.products.sort((a,b)=>a.price-b.price);if($("#sort").value==="high")d.products.sort((a,b)=>b.price-a.price);$("#products").innerHTML=d.products.map(productCard).join("")};$("#search").addEventListener("input",load);$("#sort").addEventListener("change",load);load();
}
async function loadProduct(){
 const id=new URLSearchParams(location.search).get("id"); if(!id){location.href="/static/shop.html";return}
 const d=await api("/products/"+id),p=d.product;
 $("#app").innerHTML=shell(`<main class="container"><section class="product-detail"><div class="detail-img"><img src="${p.image}" alt="${p.name}"></div><div class="detail"><div class="eyebrow">${p.category} • ${p.weight}</div><h1>${p.name}</h1><p class="desc">${p.description}</p><div class="benefits">${p.benefits.split("|").map(x=>`<span>${x.trim()}</span>`).join("")}</div><div class="price"><strong>${money(p.price)}</strong><span class="mrp">${money(p.mrp)}</span><span class="tag">${p.discount}% OFF</span></div><div class="qty"><button onclick="changeQty(-1)">−</button><input id="qty" value="1" type="number" min="1" max="${p.stock}"><button onclick="changeQty(1)">+</button></div><button class="btn gold" onclick="addProductWithQty(${p.id})">Add to cart</button><h3 style="color:var(--brown);margin-top:35px">Recommended usage</h3><p class="desc">${p.usage}</p><h3 style="color:var(--brown)">Nutrition information</h3><p class="desc">${p.nutrition}</p><p class="muted">Always follow the product label and consult a qualified professional for medical or dietary questions.</p></div></section></main>`);
 renderNav();
 window.changeQty=(n)=>{const q=$("#qty");q.value=Math.max(1,Math.min(Number(q.max),Number(q.value)+n))};
 window.addProductWithQty=async(id)=>{const p=(await api("/products/"+id)).product;const qty=Math.max(1,Math.min(p.stock,Number($("#qty").value)||1));const c=cart();const f=c.find(x=>x.product_id===id);if(f)f.quantity=Math.min(p.stock,f.quantity+qty);else c.push({product_id:id,quantity:qty,product:p});setCart(c);toast("Added to cart")};
}
function loadCart(){
 const c=cart();let sub=c.reduce((a,x)=>a+x.product.price*x.quantity,0),ship=sub>=999||sub===0?0:79,total=sub+ship;
 $("#app").innerHTML=shell(`<main class="container"><section class="page-head"><div class="eyebrow">Your selection</div><h1>Shopping Cart</h1></section>${c.length?`<div class="cart-layout"><div class="table-wrap"><table class="table"><thead><tr><th>Product</th><th>Qty</th><th>Price</th><th>Total</th><th></th></tr></thead><tbody>${c.map((x,i)=>`<tr><td><div style="display:flex;align-items:center;gap:12px"><img src="${x.product.image}" style="width:65px;height:65px;object-fit:cover;border-radius:9px"><b>${x.product.name}</b></div></td><td><input style="width:65px;padding:9px" type="number" min="1" max="${x.product.stock}" value="${x.quantity}" onchange="updateCartQty(${i},this.value)"></td><td>${money(x.product.price)}</td><td>${money(x.product.price*x.quantity)}</td><td><button class="btn small outline" onclick="removeCart(${i})">Remove</button></td></tr>`).join("")}</tbody></table></div><aside class="summary"><h3>Order summary</h3><div class="sumrow"><span>Subtotal</span><b>${money(sub)}</b></div><div class="sumrow"><span>Shipping</span><b>${ship?money(ship):"FREE"}</b></div><div class="sumtotal"><span>Total</span><span>${money(total)}</span></div><a class="btn gold" style="width:100%;margin-top:18px" href="/static/checkout.html">Proceed to checkout</a></aside></div>`:`<div class="empty"><h3>Your cart is empty</h3><p>Discover our rosehip collection.</p><a class="btn" href="/static/shop.html">Shop now</a></div>`}</main>`);
 renderNav();
 window.updateCartQty=(i,v)=>{const c=cart();c[i].quantity=Math.max(1,Math.min(c[i].product.stock,Number(v)||1));setCart(c);loadCart()};
 window.removeCart=(i)=>{const c=cart();c.splice(i,1);setCart(c);loadCart()};
}
async function loadAuth(type){
 const isLogin=type==="login";$("#app").innerHTML=shell(`<main class="container"><div class="form-card"><div class="eyebrow">${isLogin?"Welcome back":"Create account"}</div><h1>${isLogin?"Login":"Register"}</h1><div id="msg"></div><form id="authForm">${!isLogin?`<div class="field"><label>Name</label><input id="name" required></div>`:""}<div class="field"><label>Email</label><input id="email" type="email" required></div><div class="field"><label>Password</label><input id="password" type="password" required></div>${!isLogin?`<div class="field"><label>Phone</label><input id="phone"></div>`:""}<button class="btn gold" style="width:100%">${isLogin?"Login":"Create account"}</button></form><p class="muted">${isLogin?`New customer? <a href="/static/register.html" style="color:var(--gold)">Register</a>`:`Already registered? <a href="/static/login.html" style="color:var(--gold)">Login</a>`}</p></div></main>`);renderNav();
 $("#authForm").onsubmit=async e=>{e.preventDefault();try{const body={email:$("#email").value,password:$("#password").value};if(!isLogin){body.name=$("#name").value;body.phone=$("#phone").value}const d=await api("/auth/"+(isLogin?"login":"register"),{method:"POST",body:JSON.stringify(body)});localStorage.setItem("mb_token",d.token);localStorage.setItem("mb_user",JSON.stringify(d.user));location.href=d.user.role==="admin"?"/static/admin.html":"/";}catch(e){$("#msg").innerHTML=`<div class="alert">${e.message}</div>`}};
}
async function loadCheckout(){
 if(!token()){location.href="/static/login.html?next=checkout";return}
 const c=cart();if(!c.length){location.href="/static/cart.html";return}
 const sub=c.reduce((a,x)=>a+x.product.price*x.quantity,0),ship=sub>=999?0:79,total=sub+ship;
 $("#app").innerHTML=shell(`<main class="container"><section class="page-head"><div class="eyebrow">Secure checkout</div><h1>Delivery & payment</h1></section><div class="checkout-layout"><form id="checkout" class="form-card" style="margin:0;max-width:none"><div class="field"><label>Full name</label><input id="sname" required></div><div class="field"><label>Phone</label><input id="sphone" required></div><div class="field"><label>Delivery address</label><textarea id="saddress" required></textarea></div><div class="field"><label>Payment method</label><select id="payment"><option value="COD">Cash on Delivery</option><option value="ONLINE">Online Payment (Razorpay if configured)</option></select></div><div class="field"><label>Order notes</label><textarea id="notes" placeholder="Optional"></textarea></div><button class="btn gold" style="width:100%">Place order</button><div id="msg"></div></form><aside class="summary"><h3>Order summary</h3>${c.map(x=>`<div class="sumrow"><span>${x.product.name} × ${x.quantity}</span><b>${money(x.product.price*x.quantity)}</b></div>`).join("")}<div class="sumrow"><span>Shipping</span><b>${ship?money(ship):"FREE"}</b></div><div class="sumtotal"><span>Total</span><span>${money(total)}</span></div></aside></div></main>`);
 renderNav();const u=user();$("#sname").value=u?.name||"";$("#sphone").value=u?.phone||"";$("#saddress").value=u?.address||"";
 $("#checkout").onsubmit=async e=>{e.preventDefault();try{const d=await api("/orders",{method:"POST",body:JSON.stringify({items:c.map(x=>({product_id:x.product_id,quantity:x.quantity})),shipping_name:$("#sname").value,shipping_phone:$("#sphone").value,shipping_address:$("#saddress").value,payment_method:$("#payment").value,notes:$("#notes").value})});localStorage.removeItem("mb_cart");location.href="/static/profile.html?order="+d.order.id}catch(e){$("#msg").innerHTML=`<div class="alert">${e.message}</div>`}};
}
async function loadProfile(){
 if(!token()){location.href="/static/login.html";return}
 const d=await api("/auth/me"),o=await api("/orders");const u=d.user;
 $("#app").innerHTML=shell(`<main class="container"><section class="page-head"><div class="eyebrow">Account</div><h1>My Profile</h1></section><div class="checkout-layout"><form id="profile" class="form-card" style="margin:0;max-width:none"><h3>Personal details</h3><div class="field"><label>Name</label><input id="name" value="${u.name||""}" required></div><div class="field"><label>Email</label><input value="${u.email}" disabled></div><div class="field"><label>Phone</label><input id="phone" value="${u.phone||""}"></div><div class="field"><label>Address</label><textarea id="address">${u.address||""}</textarea></div><button class="btn">Save changes</button><button type="button" class="btn outline" onclick="logout()" style="margin-left:7px">Logout</button><div id="msg"></div></form><div><h2 style="font-family:'Playfair Display';color:var(--brown)">My Orders</h2>${o.orders.length?o.orders.map(x=>`<div class="card" style="padding:18px;margin-bottom:12px"><b>${x.order_number}</b><p class="muted">${new Date(x.created_at).toLocaleString()} • ${x.order_status} • ${x.payment_status}</p><strong>${money(x.total)}</strong> <a class="btn small outline" href="/api/orders/${x.id}/invoice" target="_blank">Invoice PDF</a></div>`).join(""):`<div class="empty">No orders yet.</div>`}</div></div></main>`);
 renderNav();$("#profile").onsubmit=async e=>{e.preventDefault();try{const x=await api("/auth/me",{method:"PUT",body:JSON.stringify({name:$("#name").value,phone:$("#phone").value,address:$("#address").value})});localStorage.setItem("mb_user",JSON.stringify(x.user));$("#msg").innerHTML='<div class="alert success">Profile updated.</div>'}catch(e){$("#msg").innerHTML=`<div class="alert">${e.message}</div>`}};
}
function logout(){localStorage.removeItem("mb_token");localStorage.removeItem("mb_user");location.href="/"}
async function loadAdmin(){
 if(user()?.role!=="admin"){location.href="/static/login.html";return}
 const s=await api("/admin/stats"),os=await api("/admin/orders"),ps=await api("/admin/products");
 $("#app").innerHTML=shell(`<main class="container"><section class="page-head"><div class="eyebrow">Store control</div><h1>Admin Dashboard</h1></section><div class="admin-grid"><div class="stat"><small>Orders</small><strong>${s.total_orders}</strong></div><div class="stat"><small>Revenue</small><strong>${money(s.revenue)}</strong></div><div class="stat"><small>Customers</small><strong>${s.customers}</strong></div><div class="stat"><small>Products</small><strong>${s.products}</strong></div></div><section class="section" style="padding-top:15px"><div class="heading"><h2>Orders</h2></div><div class="table-wrap"><table class="table"><thead><tr><th>Order</th><th>Customer</th><th>Total</th><th>Payment</th><th>Status</th><th>Action</th></tr></thead><tbody>${os.orders.map(o=>`<tr><td>${o.order_number}</td><td>${o.shipping_name}<br>${o.shipping_phone}</td><td>${money(o.total)}</td><td>${o.payment_status}</td><td><select id="st${o.id}"><option ${o.order_status==="Placed"?"selected":""}>Placed</option><option ${o.order_status==="Confirmed"?"selected":""}>Confirmed</option><option ${o.order_status==="Packed"?"selected":""}>Packed</option><option ${o.order_status==="Shipped"?"selected":""}>Shipped</option><option ${o.order_status==="Delivered"?"selected":""}>Delivered</option><option ${o.order_status==="Cancelled"?"selected":""}>Cancelled</option></select></td><td><button class="btn small" onclick="saveOrder(${o.id})">Save</button></td></tr>`).join("")}</tbody></table></div></section><section class="section" style="padding-top:10px"><div class="heading"><h2>Products</h2></div><div class="table-wrap"><table class="table"><thead><tr><th>Product</th><th>Price</th><th>Stock</th><th>Active</th><th>Action</th></tr></thead><tbody>${ps.products.map(p=>`<tr><td>${p.name}</td><td>${money(p.price)}</td><td>${p.stock}</td><td>${p.active?"Yes":"No"}</td><td><button class="btn small outline" onclick="disableProduct(${p.id})">Disable</button></td></tr>`).join("")}</tbody></table></div></section></main>`);
 renderNav();
 window.saveOrder=async id=>{try{await api("/admin/orders/"+id,{method:"PUT",body:JSON.stringify({order_status:$("#st"+id).value})});toast("Order updated")}catch(e){toast(e.message)}};
 window.disableProduct=async id=>{if(confirm("Disable this product?")){await api("/admin/products/"+id,{method:"DELETE"});loadAdmin()}};
}
(async()=>{
 const page=document.body.dataset.page;
 try{
  if(page==="home")await loadHome();else if(page==="shop")await loadShop();else if(page==="product")await loadProduct();
  else if(page==="cart")loadCart();else if(page==="checkout")await loadCheckout();else if(page==="login")await loadAuth("login");
  else if(page==="register")await loadAuth("register");else if(page==="profile")await loadProfile();else if(page==="admin")await loadAdmin();
 }catch(e){console.error(e);document.querySelector("#app").innerHTML=`<div class="container empty" style="margin:70px auto"><h2>Something went wrong</h2><p>${e.message}</p></div>`}
})();
