import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import matplotlib.pyplot as plt

st.image("https://calorycontrol.com.mx/staging/wp-content/uploads/2021/04/LogoHorizontal-768x210.png", use_column_width=True)

st.markdown("<h1 style='text-align: center; font-weight: bold; color: black; font-size: 48px; font-family: Montserrat;'>Tablero interactivo de desempeño</h1>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black; font-size: 16px; font-family: Montserrat;'>En este tablero veremos el desempeño historico de la empresa a lo largo de los años que se nos dio la información. Tenemos un indice en el cual ponemos todos los rubros los cuales podemos ver un análisis gráfico así como númerico del desempeño de la empresa para la ayuda de la toma de decisiones</h1>", unsafe_allow_html=True)

clientes = pd.read_csv('Clientes (SN).csv')
costos = pd.read_csv('Costos de produccion (SN).csv')
saldos = pd.read_csv('Cuentas por cobrar (SN).csv')
facturacion = pd.read_csv('Facturacion (SN).csv')
gastos = pd.read_csv('Gastos (SN).csv')

selection = st.sidebar.radio("Menú de opciones:", ('Ingresos', 'Costos' , 'Gastos' ,'Ratios'))



if selection == 'Costos':
    st.markdown("<h1 style='text-align: left; color: black; font-size: 24px; font-family: Montserrat;'>Costos</h1>", unsafe_allow_html=True)
    costos['Margen_%'] = round(costos['MARGEN_TOTAL'] / costos['SUBTOTAL_PARTIDA'] * 100, 2)
    mis_bins = [-913, 60, 70, 80, 90, 100]
    labels = ['- 60%', '60% y 70%', '70% y 80%', '80% y 90%', '+ 90%']
    costos['Margen_Q'] = pd.cut(x=costos['Margen_%'], bins=mis_bins, labels=labels, include_lowest=True)

    costo_agrup = costos.groupby(['Margen_Q', 'Año', 'Mes']).agg({'CANT': 'sum', 'COSTO_TOTAL': 'sum'})
    costo_agrup = costo_agrup.reset_index()

    C_2022 = costo_agrup[costo_agrup['Año'] == 2022].groupby(['Año', 'Mes']).agg({'CANT': 'sum', 'COSTO_TOTAL': 'sum'})
    C_2022 = C_2022.reset_index()
    C_2022['Acumulado'] = C_2022['COSTO_TOTAL'].cumsum()

    C_2023 = costo_agrup[costo_agrup['Año'] == 2023].groupby(['Año', 'Mes']).agg({'CANT': 'sum', 'COSTO_TOTAL': 'sum'})
    C_2023 = C_2023.reset_index()
    C_2023['Acumulado'] = C_2023['COSTO_TOTAL'].cumsum()

    C_NET_gruped = pd.concat([C_2022, C_2023])

    year_input = st.sidebar.multiselect(
    'Año',
    costo_agrup.groupby('Año').count().reset_index()['Año'].tolist())
    if len(year_input) > 0:
        costo_agrup = costo_agrup[costo_agrup['Año'].isin(year_input)]
        C_NET_gruped = C_NET_gruped[C_NET_gruped['Año'].isin(year_input)]


    graf1 = alt.Chart(costo_agrup).mark_bar(size=15).encode(
    x=alt.X('Mes:N', axis=alt.Axis(title='Mes', labelFontSize=12, titleFontSize=14, labelColor='black', titleColor='black')),
    y=alt.Y('sum(CANT)', axis=alt.Axis(title='Cantidad total de Ventas', labelFontSize=12, titleFontSize=14, labelColor='black', titleColor='black')),
    tooltip=['Año', 'sum(CANT)', 'Margen_Q'],
    color= alt.Color('Margen_Q:N', scale=alt.Scale(scheme='redgrey')),
    ).properties(
    width=250,
    height=300,
    title=alt.TitleParams(
        text='Desglose de Costos',
        fontSize=18,
        font='Montserrat',
        fontWeight='bold'
    )
    )

    graf2 = alt.Chart(C_NET_gruped).mark_line(color='red').encode(
        x=alt.X('Mes', axis=alt.Axis(title='Mes')),
        y=alt.Y('Acumulado', axis=alt.Axis(title='Costos')),
        tooltip=['Año', 'Mes', 'Acumulado'],
        color = alt.Color('Año:N', scale=alt.Scale(scheme='redgrey')),
    ).properties(
        width=500,
        height=300,
        title=alt.TitleParams(
            text='Costos mensuales Acumulados',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )
    
    counts = costos['NOMBRE_VENDEDOR'].value_counts()
    data = pd.DataFrame({'labels': counts.index.tolist(), 'sizes': counts.values.tolist()})
    graf3 = alt.Chart(data).mark_arc(size=200).encode(
            theta = alt.Theta(field = 'sizes', type='quantitative', title='Tamaño'),
            color = alt.Color(field = 'labels',type='nominal', scale=alt.Scale(scheme='redgrey')),
            tooltip=['labels', 'sizes']
        ).properties(
            width=250,
            height=300,
            title=alt.TitleParams(
            text='Porcentaje de Ventas de cada Vendedor en 2022',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold',
        )
    )

    top_15best = costos.groupby('DESCR')['MARGEN_TOTAL'].sum().nlargest(15)

    graf4 = alt.Chart(top_15best.reset_index()).mark_bar().encode(
        x=alt.X('MARGEN_TOTAL', axis=alt.Axis(title='Margen total')),
        y=alt.Y('DESCR', axis=alt.Axis(title='Tipo de producto'), sort='-x'),
        color=alt.Color('DESCR:N', scale=alt.Scale(scheme='redgrey')),
        tooltip=['DESCR', 'MARGEN_TOTAL']
    ).properties(
        width=500,
        height=300,
        title=alt.TitleParams(
            text='Top 15 productos con mayor margen de utilidad en 2022',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold',
    ))
    
    st.altair_chart((graf2 | graf1), use_container_width=True)
    st.altair_chart((graf3 | graf4), use_container_width=True)


if selection == 'Ingresos':
    st.markdown("<h1 style='text-align: left; color: black; font-size: 24px; font-family: Montserrat;'>Ingresos</h1>", unsafe_allow_html=True)
    facturacion = facturacion[facturacion['STATUS']!='C']
    facturacion[['Mes', 'Año', 'CVE_VEND']] = facturacion[['Mes', 'Año','CVE_VEND']].astype(str)
    facturacion['Año_Mes'] = facturacion['Año'] + facturacion['Mes'] + facturacion['CVE_VEND']
    group_facturacion = facturacion.groupby(['SERIE', 'Año_Mes', 'Año', 'Mes', 'CVE_VEND']).sum()
    group_facturacion = group_facturacion.reset_index()
    group_facturacion.SERIE.unique()

    DEV =  group_facturacion[group_facturacion['SERIE']== 'DEV']
    F = group_facturacion[group_facturacion['SERIE']== 'F']
    NC = group_facturacion[group_facturacion['SERIE']== 'NC']
    NC_F = pd.merge(DEV,NC, on ='Año_Mes',how= 'outer')
    facturacion_N = pd.merge(NC_F,F, on ='Año_Mes',how= 'outer')
    facturacion_N = facturacion_N.drop(['Año_x', 'Mes_x', 'CVE_VEND_x', 'DES_FIN_x', 'SERIE_x', 
                                        'DESCUENTO_x', 'SERIE_y', 'Año_y', 'Mes_y', 'CVE_VEND_y',
                                        'DESCUENTO_y', 'DES_FIN_y', 'SERIE','DES_FIN'], axis=1)
    facturacion_N = facturacion_N.rename(columns ={ 'CAN_TOT_x': 'Devoluciones', 'CAN_TOT_y':'Notas_Credito', 'CAN_TOT':'Facturacion'})
    facturacion_N.loc[22]=['2020128.0', 6987.500,0,2020,12,'8.0',0,0]
    facturacion_N.loc[48]=['202098.0', 9508.983,0,2020,9,'8.0',0,0]
    facturacion_N.loc[80]=['2022103.0', 70000.000	,0,2022,10,'3.0',0,0]
    facturacion_N.loc[121]=['20201212.0', 0,30172.40,2020,12,'12.0',0,0]
    facturacion_N.loc[130]=['202097.0', 0,2575.40,2020,9,'7.0',0,0]
    facturacion_N.loc[133]=['2021125.0', 0,1714.55,2021,12,'5.0',0,0]
    facturacion_N.loc[136]=['202123.0', 0,9965.00,2021,2,'3.0',0,0]
    facturacion_N.loc[137]=['202128.0', 0,7250.00,2021,2,'8.0',0,0]
    facturacion_N.loc[144]=['202158.0', 0,25438.00,2021,5,'8.0',0,0]
    facturacion_N = facturacion_N.fillna(0)
    facturacion_N[['Mes', 'Año']] = facturacion_N[['Mes', 'Año']].astype(float)
    facturacion_N['Ventas_Netas'] = facturacion_N['Facturacion']-facturacion_N['DESCUENTO']-facturacion_N['Notas_Credito']-facturacion_N['Devoluciones']
    facturacion_N.isnull().sum()

    facturacion_N = facturacion_N.reindex(columns=['Año_Mes','Año','Mes','CVE_VEND','Facturacion','Devoluciones',
                                   'Notas_Credito','DESCUENTO', 'Ventas_Netas'])

    DEV =  facturacion_N.drop(['Año_Mes','Notas_Credito','Facturacion','DESCUENTO','Ventas_Netas'], axis =1)
    DEV['Serie'] = 'Devoluciones'
    DEV = DEV.rename(columns={'Devoluciones': 'Monto'})

    F = facturacion_N.drop(['Año_Mes','Notas_Credito','Devoluciones','DESCUENTO','Ventas_Netas'], axis =1)
    F['Serie'] = 'Ventas Brutas'
    F = F.rename(columns={'Facturacion': 'Monto'})

    NC = facturacion_N.drop(['Año_Mes','Facturacion','Devoluciones','DESCUENTO','Ventas_Netas'], axis =1)
    NC['Serie'] = 'Notas de Crédito'
    NC = NC.rename(columns={'Notas_Credito': 'Monto'})

    DES = facturacion_N.drop(['Año_Mes','Notas_Credito','Devoluciones','Facturacion','Ventas_Netas'], axis =1)
    DES['Serie'] = 'Descuentos'
    DES = DES.rename(columns={'DESCUENTO': 'Monto'})

    F_NET = facturacion_N.drop(['Año_Mes','Notas_Credito','Devoluciones','Facturacion','DESCUENTO'], axis =1)
    F_NET['Serie'] = 'Ventas Netas'
    F_NET = F_NET.rename(columns={'Ventas_Netas': 'Monto'})

    facturacion_Conc = pd.concat([F_NET, NC, DES, DEV]) 

    F_NET_Grup = F_NET.groupby(['Año','CVE_VEND']).sum()
    F_NET_Grup = F_NET_Grup.reset_index()

    F_2019 =F_NET[F_NET['Año']==2019]
    F_2019 = F_2019.groupby(['Año','Mes','Serie']).sum()
    F_2019 = F_2019.reset_index()
    F_2019['Acumulado'] = F_2019['Monto'].cumsum()
    F_2020 =F_NET[F_NET['Año']==2020]
    F_2020 = F_2020.groupby(['Año','Mes','Serie']).sum()
    F_2020 = F_2020.reset_index()
    F_2020['Acumulado'] = F_2020['Monto'].cumsum()
    F_2021 =F_NET[F_NET['Año']==2021]
    F_2021 = F_2021.groupby(['Año','Mes','Serie']).sum()
    F_2021 = F_2021.reset_index()
    F_2021['Acumulado'] = F_2021['Monto'].cumsum()
    F_2022 =F_NET[F_NET['Año']==2022]
    F_2022 = F_2022.groupby(['Año','Mes','Serie']).sum()
    F_2022 = F_2022.reset_index()
    F_2022['Acumulado'] = F_2022['Monto'].cumsum()
    F_2023 =F_NET[F_NET['Año']==2023]
    F_2023 = F_2023.groupby(['Año','Mes','Serie']).sum()
    F_2023 = F_2023.reset_index()
    F_2023['Acumulado'] = F_2023['Monto'].cumsum()
    F_NET_gruped = pd.concat([F_2019, F_2020, F_2021, F_2022, F_2023])

    facturacion_Conc_N = facturacion_Conc[facturacion_Conc['Serie']!='Ventas Netas']
    facturacion_Conc_N = pd.concat([facturacion_Conc_N, F]) 
    facturacion_Conc_N = facturacion_Conc_N.groupby(['Año', 'Mes', 'Serie']).sum().reset_index()
    facturacion_Conc_N.Serie.unique()


    year_input = st.sidebar.multiselect(
    'Año',
    facturacion_Conc.groupby('Año').count().reset_index()['Año'].tolist())
    if len(year_input) > 0:
        facturacion_Conc = facturacion_Conc[facturacion_Conc['Año'].isin(year_input)]
        F_NET_gruped = F_NET_gruped[F_NET_gruped['Año'].isin(year_input)]
        facturacion_Conc_N = facturacion_Conc_N[facturacion_Conc_N['Año'].isin(year_input)]
        F_NET_Grup = F_NET_Grup[F_NET_Grup['Año'].isin(year_input)]


    graf1 = alt.Chart(facturacion_Conc).mark_bar(size=30).encode(
        x=alt.X('Año:N', axis=alt.Axis(title='Año', labelFontSize=12, titleFontSize=14, labelColor='black', titleColor='black')),
        y=alt.Y('sum(Monto)', axis=alt.Axis(title='Ventas', labelFontSize=12, titleFontSize=14, labelColor='black', titleColor='black')),
        tooltip=['Año', 'sum(Monto)', 'Serie'],
        color=alt.Color('Serie:N', scale=alt.Scale(scheme='redgrey')),
    ).properties(
        width=250,
        height=300,
        title=alt.TitleParams(
            text='Desglose de Ventas',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    graf2 = alt.Chart(F_NET_gruped).mark_line(color='red').encode(
        x=alt.X('Mes', axis=alt.Axis(title='Mes')),
        y=alt.Y('Acumulado', axis=alt.Axis(title='Ventas')),
        tooltip=['Año', 'Mes', 'Acumulado'],
        color = alt.Color('Año:N', scale=alt.Scale(scheme='redgrey')), 
    ).properties(
        width=500,
        height=300,
        title=alt.TitleParams(
            text='Ventas Netas Acumuladas',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    graf3 = alt.Chart(facturacion_Conc_N).mark_line(color='red').encode(
        x=alt.X('Mes', axis=alt.Axis(title='Mes')),
        y=alt.Y('Monto', axis=alt.Axis(title='Ventas')),
        tooltip=['Año', 'Mes', 'Serie'],
        color = alt.Color('Serie:N', scale=alt.Scale(scheme='redgrey')), 
    ).properties(
        width=500,
        height=300,
        title=alt.TitleParams(
            text='Desglose de Ingreso Mensual',
            font='Montserrat',
            fontSize=18,
            fontWeight='bold'
        )
    )

    graf4 = alt.Chart(F_NET_Grup).mark_arc().encode(
        theta=alt.Theta(field='Monto', type='quantitative', title='Devoluciones'),
        color=alt.Color(field='CVE_VEND', type='nominal', title='Vendedor', scale=alt.Scale(scheme='redgrey')),
        tooltip=['Año','Monto', 'CVE_VEND']
    ).properties(
        width=250,
        height=300,
        title=alt.TitleParams(
            text='Ventas Netas por Vendedor',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    st.altair_chart((graf2 | graf1) , use_container_width=True)
    st.altair_chart((graf4 | graf3), use_container_width=True)
    #st.altair_chart((graf2 | graf1) & (graf4 | graf3), use_container_width=True)

if selection == 'Gastos':

    st.markdown("<h1 style='text-align: left; color: black; font-size: 24px; font-family: Montserrat;'>Gastos</h1>", unsafe_allow_html=True)

    gastos = gastos[gastos['TIPO_GASTO']!= 'COMPRAS ']
    gastos = gastos[gastos['TIPO_GASTO']!= 'COMPRAS']

    lista = gastos.TIPO_GASTO.unique()
    lista.sort()

    gastos['CATEGORIA'] = np.where(gastos['TIPO_GASTO'] == lista[0], 'Gastos de administración', 
                       np.where(gastos['TIPO_GASTO'] == lista[1], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[2], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[3], 'Gastos financieros',
                       np.where(gastos['TIPO_GASTO'] == lista[4], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[5], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[6], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[7], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[8], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[9], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[10], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[11], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[12], 'Gastos financieros',
                       np.where(gastos['TIPO_GASTO'] == lista[13], 'Mixto',
                       np.where(gastos['TIPO_GASTO'] == lista[14], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[15], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[16], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[17], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[18], 'Gastos financieros',
                       np.where(gastos['TIPO_GASTO'] == lista[19], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[20], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[21], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[22], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[23], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[24], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[25], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[26], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[27], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[28], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[29], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[30], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[31], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[32], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[33], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[34], 'Mixto',
                       np.where(gastos['TIPO_GASTO'] == lista[35], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[36], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[37], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[38], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[39], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[40], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[41], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[42], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[43], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[44], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[45], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[46], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[47], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[48], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[49], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[50], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[51], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[52], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[53], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[54], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[55], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[56], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[57], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[58], 'Costo',
                       np.where(gastos['TIPO_GASTO'] == lista[59], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[60], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[61], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[62], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[63], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[64], 'Mano de Obra',
                       np.where(gastos['TIPO_GASTO'] == lista[65], 'Gastos de venta',
                       np.where(gastos['TIPO_GASTO'] == lista[66], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[67], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[68], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[69], 'Gastos de administración',
                       np.where(gastos['TIPO_GASTO'] == lista[70], 'Gastos de administración',  
                       np.where(gastos['TIPO_GASTO'] == lista[71], 'Mixto', 
                       np.where(gastos['TIPO_GASTO'] == lista[72], 'Gastos de administración',                                                                                                                                                                                                                                                                                                                                                                         
                                'Otros')))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))

    gastos = gastos[gastos['STATUS']=='Vigente']
    gastos = gastos[gastos['CATEGORIA']!='Mano de Obra']
    gastos = gastos[gastos['CATEGORIA']!='Costo']
    gastos_group = gastos.groupby(['Año', 'Mes', 'CATEGORIA']).sum().reset_index()

    G_2020 =gastos_group[gastos_group['Año']==2020]
    G_2020 = G_2020.groupby(['Año','Mes']).sum().reset_index()
    G_2020['Acumulado'] = G_2020['TOTAL'].cumsum()
    G_2021 =gastos_group[gastos_group['Año']==2021]
    G_2021 = G_2021.groupby(['Año','Mes']).sum().reset_index()
    G_2021['Acumulado'] = G_2021['TOTAL'].cumsum()
    G_2022 =gastos_group[gastos_group['Año']==2022]
    G_2022 = G_2022.groupby(['Año','Mes']).sum().reset_index()
    G_2022['Acumulado'] = G_2022['TOTAL'].cumsum()
    G_2023 =gastos_group[gastos_group['Año']==2023]
    G_2023 = G_2023.groupby(['Año','Mes']).sum().reset_index()
    G_2023['Acumulado'] = G_2023['TOTAL'].cumsum()
    G_ACUM_gruped = pd.concat([G_2020, G_2021, G_2022, G_2023])

    lista2 = gastos.groupby(['PROVEEDOR']).sum().reset_index()
    lista2 = lista2.sort_values(by=['TOTAL'])
    lista2 = lista2.tail()
    lista2 = lista2.PROVEEDOR.unique()

    gastos['Proveedor_red'] = np.where(gastos['PROVEEDOR'] == lista2[0], 'EFECTIVALE S. de R.L. de C.V.', 
                       np.where(gastos['PROVEEDOR'] == lista2[1], 'SOLUCIONES LABORALES CF S.A. DE C.V.',
                       np.where(gastos['PROVEEDOR'] == lista2[2], 'ASOCIACION DE TRABAJADORES A LA VANGUARDIA',
                       np.where(gastos['PROVEEDOR'] == lista2[3], 'FRANCISCO DE GUADALUPE NOGUERAS RUBIO',
                       np.where(gastos['PROVEEDOR'] == lista2[4], 'DH4 COMERCIALIZADORA SA DE CV',
                                'Otros')))))

    gastos_prov = gastos.groupby(['Año', 'Proveedor_red']).sum().reset_index()

    G_MP = gastos.groupby(['Año', 'MP']).sum().reset_index()

    year_input = st.sidebar.multiselect(
    'Año',
    gastos.groupby('Año').count().reset_index()['Año'].tolist())
    if len(year_input) > 0:
        gastos_group = gastos_group[gastos_group['Año'].isin(year_input)]
        G_ACUM_gruped = G_ACUM_gruped[G_ACUM_gruped['Año'].isin(year_input)]
        G_MP = G_MP[G_MP['Año'].isin(year_input)]
        gastos_prov = gastos_prov[gastos_prov['Año'].isin(year_input)]



    graf1 = alt.Chart(gastos_group).mark_bar(size=30).encode(
        x=alt.X('Mes:N', axis=alt.Axis(title='Mes', labelFontSize=12, titleFontSize=14, labelColor='black', titleColor='black')),
        y=alt.Y('sum(TOTAL)', axis=alt.Axis(title='Cantidad total de Ventas', labelFontSize=12, titleFontSize=14, labelColor='black', titleColor='black')),
        tooltip=['Mes', 'sum(TOTAL)', 'CATEGORIA'],
        color=alt.Color('CATEGORIA:N', scale=alt.Scale(scheme='redgrey')),
    ).properties(
        width=500,
        height=300,
        title=alt.TitleParams(
            text='Gastos por categoria',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    graf2 = alt.Chart(G_ACUM_gruped).mark_line(color='red').encode(
        x=alt.X('Mes', axis=alt.Axis(title='Mes')),
        y=alt.Y('Acumulado', axis=alt.Axis(title='Ventas')),
        tooltip=['Año', 'Mes', 'Acumulado'],
        color = alt.Color('Año:N', scale=alt.Scale(scheme='redgrey')), 
    ).properties(
        width=500,
        height=300,
        title=alt.TitleParams(
            text='Gastos Netos Acumulados',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    graf3 = alt.Chart(G_MP).mark_arc().encode(
        theta=alt.Theta(field='TOTAL', type='quantitative', title='Devoluciones'),
        color=alt.Color(field='MP', type='nominal', title='Vendedor', scale=alt.Scale(scheme='redgrey')),
        tooltip=['Año','TOTAL', 'MP']
    ).properties(
        width=250,
        height=300,
        title=alt.TitleParams(
            text='Gastos por Método de Pago',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    graf4 = alt.Chart(gastos_prov).mark_arc().encode(
        theta=alt.Theta(field='TOTAL', type='quantitative', title='Devoluciones'),
        color=alt.Color(field='Proveedor_red', type='nominal', title='Vendedor', scale=alt.Scale(scheme='redgrey')),
        tooltip=['Año','TOTAL', 'Proveedor_red']
    ).properties(
        width=250,
        height=300,
        title=alt.TitleParams(
            text='Gastos Anuales por Proveedor',
            fontSize=18,
            font='Montserrat',
            fontWeight='bold'
        )
    )

    st.altair_chart((graf2 | graf4 ) & (graf3 | graf1), use_container_width=True)
        
if selection == 'Ratios':
    facturacion = facturacion[facturacion['STATUS']!='C']
    facturacion[['Mes', 'Año', 'CVE_VEND']] = facturacion[['Mes', 'Año','CVE_VEND']].astype(str)
    facturacion['Año_Mes'] = facturacion['Año'] + facturacion['Mes'] + facturacion['CVE_VEND']
    group_facturacion = facturacion.groupby(['SERIE', 'Año_Mes', 'Año', 'Mes', 'CVE_VEND']).sum()
    group_facturacion = group_facturacion.reset_index()
    group_facturacion.SERIE.unique()

    DEV =  group_facturacion[group_facturacion['SERIE']== 'DEV']
    F = group_facturacion[group_facturacion['SERIE']== 'F']
    NC = group_facturacion[group_facturacion['SERIE']== 'NC']
    NC_F = pd.merge(DEV,NC, on ='Año_Mes',how= 'outer')
    facturacion_N = pd.merge(NC_F,F, on ='Año_Mes',how= 'outer')
    facturacion_N = facturacion_N.drop(['Año_x', 'Mes_x', 'CVE_VEND_x', 'DES_FIN_x', 'SERIE_x', 
                                        'DESCUENTO_x', 'SERIE_y', 'Año_y', 'Mes_y', 'CVE_VEND_y',
                                        'DESCUENTO_y', 'DES_FIN_y', 'SERIE','DES_FIN'], axis=1)
    facturacion_N = facturacion_N.rename(columns ={ 'CAN_TOT_x': 'Devoluciones', 'CAN_TOT_y':'Notas_Credito', 'CAN_TOT':'Facturacion'})
    facturacion_N.loc[22]=['2020128.0', 6987.500,0,2020,12,'8.0',0,0]
    facturacion_N.loc[48]=['202098.0', 9508.983,0,2020,9,'8.0',0,0]
    facturacion_N.loc[80]=['2022103.0', 70000.000	,0,2022,10,'3.0',0,0]
    facturacion_N.loc[121]=['20201212.0', 0,30172.40,2020,12,'12.0',0,0]
    facturacion_N.loc[130]=['202097.0', 0,2575.40,2020,9,'7.0',0,0]
    facturacion_N.loc[133]=['2021125.0', 0,1714.55,2021,12,'5.0',0,0]
    facturacion_N.loc[136]=['202123.0', 0,9965.00,2021,2,'3.0',0,0]
    facturacion_N.loc[137]=['202128.0', 0,7250.00,2021,2,'8.0',0,0]
    facturacion_N.loc[144]=['202158.0', 0,25438.00,2021,5,'8.0',0,0]
    facturacion_N = facturacion_N.fillna(0)
    facturacion_N[['Mes', 'Año']] = facturacion_N[['Mes', 'Año']].astype(float)
    facturacion_N['Ventas_Netas'] = facturacion_N['Facturacion']-facturacion_N['DESCUENTO']-facturacion_N['Notas_Credito']-facturacion_N['Devoluciones']
    facturacion_N.isnull().sum()

    facturacion_N = facturacion_N.reindex(columns=['Año_Mes','Año','Mes','CVE_VEND','Facturacion','Devoluciones',
                                   'Notas_Credito','DESCUENTO', 'Ventas_Netas'])

    DEV =  facturacion_N.drop(['Año_Mes','Notas_Credito','Facturacion','DESCUENTO','Ventas_Netas'], axis =1)
    DEV['Serie'] = 'Devoluciones'
    DEV = DEV.rename(columns={'Devoluciones': 'Monto'})

    F = facturacion_N.drop(['Año_Mes','Notas_Credito','Devoluciones','DESCUENTO','Ventas_Netas'], axis =1)
    F['Serie'] = 'Ventas Brutas'
    F = F.rename(columns={'Facturacion': 'Monto'})

    NC = facturacion_N.drop(['Año_Mes','Facturacion','Devoluciones','DESCUENTO','Ventas_Netas'], axis =1)
    NC['Serie'] = 'Notas de Crédito'
    NC = NC.rename(columns={'Notas_Credito': 'Monto'})

    DES = facturacion_N.drop(['Año_Mes','Notas_Credito','Devoluciones','Facturacion','Ventas_Netas'], axis =1)
    DES['Serie'] = 'Descuentos'
    DES = DES.rename(columns={'DESCUENTO': 'Monto'})

    F_NET = facturacion_N.drop(['Año_Mes','Notas_Credito','Devoluciones','Facturacion','DESCUENTO'], axis =1)
    F_NET['Serie'] = 'Ventas Netas'
    F_NET = F_NET.rename(columns={'Ventas_Netas': 'Monto'})

    facturacion_Conc = pd.concat([F_NET, NC, DES, DEV]) 

    F_NET_Grup = F_NET.groupby(['Año','CVE_VEND']).sum()
    F_NET_Grup = F_NET_Grup.reset_index()
    
    years_filter = st.selectbox("Selecciona el año que deseas analizar:", pd.unique(F_NET["Año"]))
    placeholder = st.empty()

    # Aplicar filtro por año seleccionado
    facturacion_filtrada = F_NET[F_NET['Año'] == years_filter]
    
    
    # ratios diseño
    ventas = facturacion_filtrada['Monto'].sum()
    cxc = saldos['MONTO ADEUDADO'].sum()
    r1 = ventas / cxc

    fijo = gastos[(gastos['TIPO_GASTO'].isin(['MAQUINARIA', 'COMPRAS', 'MAQUILAS GIC', 'MOBILIARIO', 'COMPRA COMPUTADORA', 'COMPRA TABLET']))]['IMPORTE'].sum()
    r2 = ventas / fijo

    un = ventas - gastos['TOTAL'].sum()
    r3 = un / ventas

    with placeholder.container():
        ratio1, ratio2, ratio3 = st.columns(3)
        ratio1.metric(
            label="Rotacion de cuentas por cobrar 💲",
            value=f"{round(r1)}x",  # x = veces
            # delta=round(r1) - 10,
        )

        ratio2.metric(
            label="Rotacion de activos 🔄",
            value=f"{round(r2)}x",  # x = veces
        )

        ratio3.metric(
            label="Margen Neto 📊",
            value=f"{round(r3, 2)}%",  # % = porcentaje
            # delta=-round(r3 / r3) * 100,
        )

st.sidebar.write("""Miembros del equipo:

Amairany Rodríguez | A01702927

Renata Chavez | A01351716

Luis Pablo Padilla Barbosa | A00572040 """)