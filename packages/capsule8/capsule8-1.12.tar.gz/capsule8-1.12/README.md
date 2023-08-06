# Capsule8 api-python

This repo is as a wrapper repo around the [Capsule8](https://github.com/capsule8/capsule8) sensor api to easily facilitate telemetry collection.

## Install with pip

```
pip install --user capsule8
```

## Install with virtualenv

```
virtualenv test_capsule8
cd test_capsule8
source bin/activate
pip install --user capsule8
```

## Testing

To test capsule8 and all it's packages run

```
make test
```

## Examples

In order to run the examples you need to have a running [capsule8](https://github.com/capsule8/capsule8) sensor on your machine. Once you have a running sensor you can run the examples. Be sure that the capsule8 sensor socket chowned by the current user.

```
sudo chown $USER /var/run/capsule8/sensor.sock
python3 examples/print_process_events.py
```

And you should see output similar to
```
events {
  event {
    id: "aaf19f70cae7b2018f7d55237bd4e0f80ca06d39a0c1876efb481caf42f302b3"
    process_id: "f0dcdb8c5ad84874a7f210326353a5d8fef331f137fc167d25e09ec7c762ad07"
    process_pid: 19959
    sensor_id: "17f25eddd795798d57990b7cb33721ecbe1774ee96a195acfd2f0d84edc67f26"
    sensor_sequence_number: 97
    sensor_monotime_nanos: 24165408812
    process {
      type: PROCESS_EVENT_TYPE_FORK
      fork_child_pid: 9443
    }
    credentials {
      uid: 1001
      gid: 1001
      euid: 1001
      egid: 1001
      suid: 1001
      sgid: 1001
      fsuid: 1001
      fsgid: 1001
    }
    process_tgid: 19959
  }
}

events {
  event {
    id: "53f5e4fbef0ee56acb97074553a0c137c4cb12e626b9b864252efb570562df7f"
    process_id: "046ace5eda2fe335cabe4c9cc11ce626563677181297f38a837ba3a7cad17964"
    process_pid: 9443
    sensor_id: "17f25eddd795798d57990b7cb33721ecbe1774ee96a195acfd2f0d84edc67f26"
    sensor_sequence_number: 98
    sensor_monotime_nanos: 24170786264
    process {
      type: PROCESS_EVENT_TYPE_FORK
      fork_child_pid: 9444
    }
    cpu: 3
    credentials {
      uid: 1001
      gid: 1001
      euid: 1001
      egid: 1001
      suid: 1001
      sgid: 1001
      fsuid: 1001
      fsgid: 1001
    }
    process_tgid: 9443
  }
}
```

## gRPC Usage

If you want more fine grain control with the gRPC protos use the `capsule8.api.v0` package. For usage on how to use generated gRPC code, follow [gRPC basics](https://grpc.io/docs/tutorials/basic/python.html).

## Build new protos

In case of an update to the capsule8 api, running `make protos` will create new generated importable python module

## CI

To deploy the capsule8 package on pypi use the script `/bin/deploy-pypi` to upload the package to pypi for other to use `pip install capsule8`.