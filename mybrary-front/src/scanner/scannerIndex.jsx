import React, { useState } from "react";
import Scanner from "./Scanner";
import {Grid} from "@mui/material";
import axios from "axios";
import {useDispatch} from "react-redux";
import store from "../store/index.js";
import {connect} from "react-redux";
import {updateErr, updateIsbn} from "../store/createSlice.js";


const ScannerIndex = (props) => {

    const dispatch = useDispatch();

    const [camera, setCamera] = useState(true);
    const [result, setResult] = useState(null);

    const onDetected = result => {
        setResult(result);
        setCamera(!camera)

        axios.post('http://localhost:8000/user/books/register/?isbn=' + result, {
            headers: {}}).then((response) => {
            if (response.status === 200) {
                // dispatch(updateIsbn(store, {payload: result}))
                console.log(response.status)
                window.location.href = '/book/register_confirm/'
            } else{
                // dispatch(updateErr(store, {payload: response.data.detail.toString()}))
                console.log(response.status)
                window.location.href = '/book/register/'
            }
        }).catch((err) => {
            console.log(err.message.toString())
            // dispatch(updateErr(store, {payload: err.message.toString()}))
            console.log(err)
            window.location.href = '/book/register/'
        })

    };

    return (
        <section className="section-wrapper">
            <div className="section-title">
                <h1 className="section-title-text">
                    {camera ? <Grid container direction='column' justifyContent='center' alignContent='center'>
                        <Grid item>
                            <Scanner onDetected={onDetected} width={props.width}/>
                        </Grid>
                    </Grid> : <p>読み込み中...</p> }
                </h1>
            </div>
        </section>
    );
}


export default ScannerIndex